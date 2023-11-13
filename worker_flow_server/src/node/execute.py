import base64
import json
import os
import sys
import traceback

from src.node import NODE_CLASS_MAPPINGS
from src.worker.task_status import TaskStatus
from src.worker.worker_error import WorkerStatusError


class WorkerExecutor:
    def __init__(self, mark="custom"):
        self.mark = mark
        self.worker_flow = {}
        self.object_storage = {}

    def get_worker_flow_json(self):
        try:
            with open(f"src/config/worker_flow/{self.mark}.json", "r") as f:
                self.worker_flow = json.load(f)
        except:
            pass

    @staticmethod
    def handle_execution_error(prompt, executed, error):
        node_id = error["node_id"]
        code = error["code"]
        class_type = prompt[node_id]["class_type"]

        mes = {
            "node_id": node_id,
            "node_type": class_type,
            "executed": list(executed),
            # "exception_message": error["exception_message"],
            # "exception_type": error["exception_type"],
            # "traceback": error["traceback"],
            # "current_inputs": error["current_inputs"],
            # "current_outputs": error["current_outputs"],
        }
        res = {"code": code, "message": f'worker 任务流执行失败 {error["exception_message"]}', "error_data": mes}
        return res

    def execute_flow(self):
        if not self.worker_flow:
            return {"code": TaskStatus.WORKER_FLOW_NOT.value, "message": "worker 任务流未配置"}

        prompt = self.worker_flow["prompt"]
        extra_data = self.worker_flow["extra_data"]

        executed = set()
        to_execute = []

        valid, error, execute_outputs, node_errors = validate_prompt(prompt) # 校验prompt 并输出输出节点

        if not valid:
            return {"code": TaskStatus.WORKER_FLOW_VALID_FAIL.value, "message": "worker 任务流验证失败",
                    "error_data": node_errors}

        for node_id in execute_outputs:
            to_execute += [(0, node_id)]
        output = {}

        while len(to_execute) > 0:
            to_execute = sorted(
                list(map(lambda a: (len(recursive_will_execute(prompt, a[-1])), a[-1]), to_execute)))
            output_node_id = to_execute.pop(0)[-1]

            success, error = recursive_execute(prompt, output, output_node_id, executed, self.object_storage) # 执行节点
            if success is not True:
                return self.handle_execution_error(prompt, executed, error)
        return {"code": TaskStatus.SUCCESS.value, "message": "", "data": output[output_node_id][0][0]}


def recursive_will_execute(prompt, current_item):
    unique_id = current_item
    inputs = prompt[unique_id]['inputs']
    will_execute = []

    for x in inputs:
        input_data = inputs[x]
        if isinstance(input_data, list):
            input_unique_id = input_data[0]
            will_execute += recursive_will_execute(prompt, input_unique_id)

    return will_execute + [unique_id]


def get_input_data(inputs, class_def, outputs={}):
    valid_inputs = class_def.INPUT_TYPES()  # 获取类定义中的有效输入类型
    input_data_all = {}  # 初始化输入数据
    for x in inputs:
        input_data = inputs[x]
        if isinstance(input_data, list):
            input_unique_id = input_data[0]
            output_index = input_data[1]
            if input_unique_id not in outputs:
                input_data_all[x] = (None,)
                continue
            obj = outputs[input_unique_id][output_index]
            input_data_all[x] = obj
        else:
            if ("required" in valid_inputs and x in valid_inputs["required"]) or (
                    "optional" in valid_inputs and x in valid_inputs["optional"]):
                input_data_all[x] = [input_data]

    return input_data_all


def map_node_over_list(obj, input_data_all):
    """
    遍历输入数据
    :param obj:
    :param input_data_all:
    :return:
    """
    max_len_input = max(len(x) for x in input_data_all.values()) if input_data_all else 0
    results = []
    if max_len_input == 0:
        results.append(obj.execute())
    else:
        for i in range(max_len_input):
            results.append(obj.execute(**{k: v[i if len(v) > i else -1] for k, v in input_data_all.items()}))
    return results


def get_output_data(obj, input_data_all):
    """
    获取输出数据
    :param obj:
    :param input_data_all:
    :return:
    """
    results = []
    return_values = map_node_over_list(obj, input_data_all)

    for r in return_values:
        results.append(r)

    output = []
    if len(results) > 0:
        output_is_list = [False] * len(results[0])
        for i, is_list in zip(range(len(results[0])), output_is_list):
            if is_list:
                output.append([x for o in results for x in o[i]])
            else:
                output.append([o[i] for o in results])

    return output


def full_type_name(klass):
    """
    获取类的全名，包括模块名
    """
    # 获取类的模块名
    module = klass.__module__
    # 如果模块名为'builtins'，则直接返回类的限定名
    if module == 'builtins':
        return klass.__qualname__
    # 否则，返回模块名和类的限定名，中间用'.'连接
    return module + '.' + klass.__qualname__


def format_value(x):
    """
    格式化值
    :param x:
    :return:
    """
    if x is None:
        return None
    elif isinstance(x, (int, float, bool, str)):
        return x
    else:
        return str(x)


def recursive_execute(prompt, outputs, current_item, executed, object_storage):
    """
    递归执行
    :param prompt:
    :param outputs:
    :param current_item:
    :param executed:
    :param object_storage:
    :return:
    """
    unique_id = current_item  # 获取唯一ID
    inputs = prompt[unique_id]['inputs']  # 获取输入字典
    class_type = prompt[unique_id]['class_type']  # 获取类类型
    class_def = NODE_CLASS_MAPPINGS[class_type]  # 获取类定义
    if unique_id in outputs:
        return True, None

    for x in inputs:  # 遍历输入字典
        input_data = inputs[x]  # 获取输入数据

        if isinstance(input_data, list):  # 如果输入数据是列表类型 递归调用
            input_unique_id = input_data[0]  # 获取输入数据的第一个元素
            if input_unique_id not in outputs:  # 如果输入数据的第一个元素不在输出字典中
                result = recursive_execute(prompt, outputs, input_unique_id, executed,
                                           object_storage)  # 递归调用
                if not result[0]:  # 如果递归调用结果为False
                    # Another node failed further upstream
                    return result  # 返回递归调用结果
    print(class_type)

    input_data_all = None  # 初始化输入数据
    try:
        input_data_all = get_input_data(inputs, class_def, outputs)  # 获取输入数据

        obj = object_storage.get((unique_id, class_type), None)  # 获取对象
        if obj is None:
            obj = class_def()  # 实例化对象
            object_storage[(unique_id, class_type)] = obj  # 存储对象

        output_data = get_output_data(obj, input_data_all)  # 执行节点方法
        outputs[unique_id] = output_data  # 存储节点输出数据
    except Exception as ex:
        typ, _, tb = sys.exc_info()
        exception_type = full_type_name(typ)
        input_data_formatted = {}
        if input_data_all is not None:
            input_data_formatted = {}
            for name, inputs in input_data_all.items():
                input_data_formatted[name] = [format_value(x) for x in inputs]

        output_data_formatted = {}
        for node_id, node_outputs in outputs.items():
            output_data_formatted[node_id] = [[format_value(x) for x in l] for l in node_outputs]

        code = ex.status_code if isinstance(ex, WorkerStatusError) else TaskStatus.WORKER_FAIL.value

        error_details = {
            "code": code,
            "node_id": unique_id,
            "exception_message": str(ex),
            "exception_type": exception_type,
            "traceback": traceback.format_tb(tb),
            "current_inputs": input_data_formatted,
            "current_outputs": output_data_formatted
        }
        return False, error_details

    executed.add(unique_id)  # 添加到已执行列表

    return True, None


def validate_prompt(prompt):
    """
    验证 prompt
    """
    outputs = set()  # 去重，用于存储输出节点

    # 遍历所有节点找出输出节点，添加到 outputs
    for x in prompt:
        class_ = NODE_CLASS_MAPPINGS[prompt[x]['class_type']]
        # 动态实例化 class
        if hasattr(class_, 'OUTPUT_NODE') and class_.OUTPUT_NODE == True:  # 判断是否是输出节点，如果是输出节点，就加入到 outputs
            outputs.add(x)

    # 如果没有输出节点，就返回错误
    if len(outputs) == 0:
        error = {
            "type": "prompt_no_outputs",  # 提示没有输出节点
            "message": "无输出节点",
            "details": "",
            "extra_info": {}
        }
        return False, error, [], []

    good_outputs = set()  # 去重，用于存储最终的输出节点
    errors = []  # 存储错误
    node_errors = {}  # 存储节点错误
    validated = {}  # 存储已验证的节点
    for o in outputs:  # 遍历所有输出节点（存在多个输出节点的情况）
        try:
            # 通过输出节点递归验证所有输入节点
            m = validate_inputs(prompt, o, validated)
            valid = m[0]
            reasons = m[1]
        except Exception as ex:  # 验证过程中出现异常
            typ, _, tb = sys.exc_info()
            valid = False
            exception_type = full_type_name(typ)  # 异常类型
            reasons = [{
                "type": "exception_during_validation",
                "message": "验证节点时出现异常",
                "details": str(ex),
                "extra_info": {
                    "exception_type": exception_type,
                    "traceback": traceback.format_tb(tb)
                }
            }]
            validated[o] = (False, reasons, o)

        if valid:  # 验证通过
            good_outputs.add(o)  # 添加到 good_outputs
        else:  # 验证失败
            # print(f"无法验证输出提示 {o}:")
            # if reasons:  # 判断错误列表是否为空，如果不为空则循环打印错误
            #     print("* (prompt):")
            #     for reason in reasons:
            #         print(f"  - {reason['message']}: {reason['details']}")
            errors += [(o, reasons)]  # 将错误添加到 errors 列表中
            for node_id, result in validated.items():
                valid = result[0]  # 获取验证结果
                reasons = result[1]  # 获取错误列表
                # 如果上游节点有错误，下游节点也会被报告为无效，但不会附加错误
                # 因此不将这些节点作为响应中的有错误的节点返回
                if not valid and reasons:  # 如果验证结果不为True且错误列表长度大于0
                    if node_id not in node_errors:  # 如果节点ID不在节点错误字典中
                        class_type = prompt[node_id]['class_type']  # 获取节点的类类型
                        node_errors[node_id] = {
                            "errors": reasons,
                            "dependent_outputs": [],
                            "class_type": class_type
                        }
                        # print(f"* {class_type} {node_id}:")
                        # for reason in reasons:  # 循环打印错误
                        #     print(f"  - {reason['message']}: {reason['details']}")
                    node_errors[node_id]["dependent_outputs"].append(o)  # 将当前节点的输出添加到节点错误字典中
            # print("Output will be ignored")

    if not good_outputs:  # 如果没有输出节点
        errors_list = []  # 存储错误列表
        for o, errors in errors:  # 遍历错误列表
            for error in errors:  # 遍历错误
                errors_list.append(f"{error['message']}: {error['details']}")
        errors_list = "\n".join(errors_list)  # 将错误列表转换为字符串

        error = {
            "type": "prompt_outputs_failed_validation",
            "message": "提示输出验证失败",
            "details": errors_list,
            "extra_info": {}
        }

        return False, error, list(good_outputs), node_errors  # 返回错误信息

    return True, None, list(good_outputs), node_errors  # 返回验证通过的输出节点


def validate_inputs(prompt, item, validated):
    """
    验证输入节点的输入
    """
    unique_id = item  # 获取唯一ID
    if unique_id in validated:  # 如果唯一ID在已验证字典中
        return validated[unique_id]  # 返回已验证字典中的结果

    inputs = prompt[unique_id]['inputs']  # 获取输入字典
    class_type = prompt[unique_id]['class_type']  # 获取类类型
    obj_class = NODE_CLASS_MAPPINGS[class_type]  # 获取类定义

    class_inputs = obj_class.INPUT_TYPES()  # 获取类定义中的有效输入类型
    required_inputs = class_inputs['required']  # 获取类定义中的必需输入类型

    errors = []  # 存储错误的列表
    valid = True  # 设置验证结果为True

    for x in required_inputs:  # 遍历必需输入类型字典
        if x not in inputs:  # 如果当前必需输入不在输入字典中
            error = {
                "type": "required_input_missing",
                "message": "缺少必需的输入",
                "details": f"{x}",
                "extra_info": {
                    "input_name": x
                }
            }
            errors.append(error)  # 将错误添加到错误列表中
            continue  # 跳过当前循环

        val = inputs[x]  # 获取当前输入的值
        info = required_inputs[x]  # 获取当前输入的信息
        type_input = info[0]  # 获取当前输入的类型
        if isinstance(val, list):  # 如果当前输入的值是列表类型
            if len(val) != 2:  # 如果当前输入的值的长度不为2
                error = {
                    "type": "bad_linked_input",
                    "message": "错误的链接输入，必须是 [node_id、slot_index] 的长度为 2 的列表",
                    "details": f"{x}",
                    "extra_info": {
                        "input_name": x,
                        "input_config": info,
                        "received_value": val
                    }
                }
                errors.append(error)  # 将错误添加到错误列表中
                continue  # 跳过当前循环

            o_id = val[0]  # 获取当前输入的值的第一个元素ID
            o_class_type = prompt[o_id]['class_type']  # 通过ID获取当前输入的值的第一个元素的类型
            r = NODE_CLASS_MAPPINGS[o_class_type].RETURN_TYPES  # 获取当前输入的值的第一个元素的返回类型
            if r[val[1]] != type_input:  # 如果当前输入的值的第二个元素的返回类型不等于当前输入的类型
                received_type = r[val[1]]  # 获取当前输入的值的第二个元素的返回类型
                details = f"{x}, {received_type} != {type_input}"  # 设置错误详情
                error = {
                    "type": "return_type_mismatch",
                    "message": "链接节点之间的返回类型不匹配",
                    "details": details,
                    "extra_info": {
                        "input_name": x,
                        "input_config": info,
                        "received_type": received_type,
                        "linked_node": val
                    }
                }
                errors.append(error)  # 将错误添加到错误列表中
                continue  # 跳过当前循环
            try:
                r = validate_inputs(prompt, o_id, validated)  # 验证当前输入的值的元素
                if not r[0]:  # 判断验证结果是否为False
                    # `r` will be set in `validated[o_id]` already
                    valid = False
                    continue  # 跳过当前循环
            except Exception as ex:  # 如果验证过程中出现异常
                typ, _, tb = sys.exc_info()  # 获取异常信息
                valid = False
                exception_type = full_type_name(typ)  # 获取异常类型
                reasons = [{
                    "type": "exception_during_inner_validation",
                    "message": "验证内部节点时出现异常",
                    "details": str(ex),
                    "extra_info": {
                        "input_name": x,
                        "input_config": info,
                        "exception_message": str(ex),
                        "exception_type": exception_type,
                        "traceback": traceback.format_tb(tb),
                        "linked_node": val
                    }
                }]
                validated[o_id] = (False, reasons, o_id)  # 将验证结果添加到已验证字典中
                continue  # 跳过当前循环
        else:
            try:
                if type_input == "INT":  # 如果当前输入的类型为INT
                    val = int(val)
                    inputs[x] = val
                if type_input == "FLOAT":  # 如果当前输入的类型为FLOAT
                    val = float(val)
                    inputs[x] = val
                if type_input == "STRING":  # 如果当前输入的类型为STRING
                    val = str(val)
                    inputs[x] = val
                if type_input == "BS64":
                    val = base64.b64decode(val)
                    inputs[x] = val
                # if type_input == "LOCAL_PATH":
                #     val = os.path.abspath(val)
                #     inputs[x] = val
                # if type_input == "CDN_PATH":
                #     val = os.path.abspath(val)
                #     inputs[x] = val
                if type_input == "JSON":
                    val = json.loads(val)
                    inputs[x] = val
            except Exception as ex:  # 如果转换过程中出现异常
                error = {
                    "type": "invalid_input_type",
                    "message": f"无法将输入值转换为 {type_input} 值",
                    "details": f"{x}, {val}, {ex}",
                    "extra_info": {
                        "input_name": x,
                        "input_config": info,
                        "received_value": val,
                        "exception_message": str(ex)
                    }
                }
                errors.append(error)
                continue

    if len(errors) > 0 or valid is not True:  # 如果错误列表长度大于0或者验证结果不为True
        ret = (False, errors, unique_id)  # 设置验证结果为False
    else:  # 如果错误列表长度不大于0且验证结果为True
        ret = (True, [], unique_id)  # 设置验证结果为True

    validated[unique_id] = ret  # 将验证结果添加到已验证字典中
    return ret  # 返回验证结果
