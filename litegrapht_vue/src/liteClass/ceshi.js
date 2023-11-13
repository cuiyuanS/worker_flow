function Ceshisuibian() {
    this.addInput("string", "image");
    this.addOutput("bool", "boolean");
    this.addProperty("value", true);
    this.widget = this.addWidget("toggle", "value", true, "value");
    this.serialize_widgets = false;
    this.widgets_up = true;
    this.size = [500, 100];
}

Ceshisuibian.prototype.getInputData = (e) => {
    console.log("接收到数据：", e)
}
Ceshisuibian.type = "ceshi/Cs2";
export default Ceshisuibian