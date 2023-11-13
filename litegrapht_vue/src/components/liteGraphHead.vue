<template>
  <div class="container">
    <button @click="downLoad" class="headButton">下载</button>
    <button @click="liteGraphSetup" class="headButton">执行</button>
  </div>
</template>

<script setup>
// import { LiteGraph } from "litegraph.js";
import { defineEmits } from "vue";
const emit = defineEmits(["downLoad","liteGraphSetup"]);
const downLoad = () => {
  emit("downLoad");
};
const liteGraphSetup = () => {
  emit("liteGraphSetup");
}
</script>

<style scoped>
.container {
  position: fixed;
  top: 0;
  left: 0;
}

.headButton{
  margin: 10px;
  width: 100px;
  height: 50px;
}
</style>
