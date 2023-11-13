import LiteGraph from "litegraph.js";
let newNode = {}
let myClass = [];


// 根据接口返回的节点数据 创建新的节点
/**
 * 
 * @param {要创建的节点} key 
 * @returns 
 */
function creatNode(key) {
    let { input, output, output_name, name, output_node } = newNode[key]
    function newLiteGraphNode() {
        if (typeof output == "object") {
            output.forEach((item, index) => {
                console.log(item)
                this.addOutput(output_name[index], item);
            });
        } else {
            this.addOutput(output, output_name);
        }
        for (let key in input.required) {
            if (typeof input.required[key][0] == "string") {
                if (input.required[key][1]) {
                    this.widget = this.addWidget("text", key, input.required[key][1].default, "value");
                    this.properties = { inputType: 'text' }
                } else {
                    this.addInput(key, input.required[key][0]);
                }
            } else {
                let values = [...input.required[key]].join(";").replaceAll(',', ';')
                this.properties = { value: input.required[key][0][0], values: values, inputType: 'combo' }
                this._values = this.properties.values.split(";");
                var that = this;
                this.widget = this.addWidget("combo", key, this.properties.value, function (v) {
                    that.properties.value = v;
                    that.triggerSlot(1, v);
                }, { property: "value", values: this._values });
            }
            this.properties = { ...this.properties, keyName: key, name }
        }
        this.serialize_widgets = true; // 默认情况下，在存储节点状态时，Widget 的值不会序列化，但如果您想存储 widget 的值
        this.widgets_up = false;  // 小部件不会在插槽之后启动
        this.output_node = output_node
    }
    newLiteGraphNode.title = name;
    return newLiteGraphNode
}

function handleCustomClass() {
    const req = require.context('./', true, /\.js$/);
    req.keys().forEach(item => {
        if (!['index.js'].includes(item.split('/')[1])) {
            myClass.push({ type: req(item).default?.type || "default/defaultName", nodeClass: req(item).default })
        }
    })
}

function detailNode(name) {
    for(let item in LiteGraph.LiteGraph.registered_node_types){
        LiteGraph.LiteGraph.unregisterNodeType(item)
    }
}

/**
 * 
 * @param {要创建的节点数据} data 
 * @param {是否删除原来的节点,默认不删除} isDetailNode 
 */
export function addNodeClass(data ,isDetailNode = false) {
    if (isDetailNode) detailNode()
    newNode = data;
    for (let key in newNode) {
        myClass.push({ type: `${newNode[key].category}/${newNode[key].name}`, nodeClass: creatNode(key) })
    }
    // handleCustomClass()
    myClass.forEach(item => {
        LiteGraph.LiteGraph.registerNodeType(item.type, item.nodeClass);
    })
}

export default myClass 