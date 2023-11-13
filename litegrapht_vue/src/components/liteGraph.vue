<!--
 * @Author: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
 * @Date: 2023-10-13 10:30:57
 * @LastEditors: error: error: git config user.name & please set dead value or install git && error: git config user.email & please set dead value or install git & please set dead value or install git
 * @LastEditTime: 2023-10-16 17:25:13
 * @FilePath: \vue-flow-admin\src\components\liteGraph.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<template>
  <div class="content">
    <div class="editor-area">
      <canvas
        class="graphcanvas"
        id="mycanvas"
        :width="screenWidth"
        :height="screenHeight"
        tabindex="10"
      ></canvas>
    </div>
  </div>
  <liteGraphHead
    @downLoad="downLoad"
    @liteGraphSetup="liteGraphSetup"
  ></liteGraphHead>
</template>

<script setup>
import LiteGraph from "litegraph.js";
import { onMounted, ref } from "vue";
import graphJson from "./graph.JSON";
import liteGraphHead from "./liteGraphHead.vue";
import { addNodeClass } from "@/liteClass/index";
import axios from "axios";

const baseUrl = "/extensions";
const screenWidth = ref(0);
const screenHeight = ref(0);
const mycanvas = ref(null);
let graph = ref(null);

async function requestContextNode() {
  const {
    data: { data, err },
  } = await axios.get(baseUrl + "/node_info");
  if (!err) {
    addNodeClass(data, true);
    createCanvas();
  }
}
// 点击执行调用的方法
async function requestNodeExecute(params) {
  const {
    data: { data, err },
  } = await axios.post(baseUrl + "/try_execute", params);
  if (!err) {
    console.warn(data);
  }
}
onMounted(() => {
  screenWidth.value = window.innerWidth;
  screenHeight.value = window.innerHeight;
  requestContextNode();
});

/* 创建 LiteGraph 实例 */
const createCanvas = () => {
  graph.value = new LiteGraph.LGraph({
    container: mycanvas.value,
    width: screenWidth.value,
    height: screenHeight.value,
    ...graphJson,
  });

  new LiteGraph.LGraphCanvas("#mycanvas", graph.value);
};

const downLoad = () => {
  var data = JSON.stringify(graph.value.serialize());
  var file = new Blob([data]);
  var url = URL.createObjectURL(file);
  var element = document.createElement("a");
  element.setAttribute("href", url);
  element.setAttribute("download", `${new Date().getTime()}.JSON`);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
  setTimeout(function () {
    URL.revokeObjectURL(url);
  }, 1000 * 60);
};

const liteGraphSetup = () => {
  var nodes = graph.value?.serialize()?.nodes;
  console.warn(nodes);
  let linkKeyMap = new Map(
    nodes
      .map((item) => {
        return item.outputs.reduce((firArr, output) => {
          console.warn();
          firArr.push([
            item.id + "-" + (output?.slot_index ?? "end"),
            output.links,
          ]);
          return firArr;
        }, []);
      })
      .flat(1)
  );
  console.info(linkKeyMap);
  let obj = nodes.reduce((firObj, item) => {
    firObj[item.id] = {
      class_type: item.properties.name,
      inputs: {},
    };
    if (item.inputs) {
      item.inputs.forEach((input) => {
        for (let i of linkKeyMap) {
          let key = i[0];
          let val = i[1];
          if (val && Array.from(val).includes(input.link)) {
            let id = key.split("-")[0];
            let idx = key.split("-")[1];
            firObj[item.id].inputs[input.name] = [id, idx * 1];
          }
        }
      });
    }
    let { inputType, keyName } = item.properties;
    if (inputType) {
      firObj[item.id].inputs[keyName] = item.widgets_values.join("");
    }
    return firObj;
  }, {});
  requestNodeExecute({
    prompt: obj,
    extra_data: graph.value?.serialize(),
  });
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped></style>
