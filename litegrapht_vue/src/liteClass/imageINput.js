/**
 * 上传图片节点
 */
function CustomImageInputNode() {
    var that = this
    // this.addInput("Image", "image");  
    this.addOutput("Image", "image");
    this.properties = { precision: 1 };
    this.value = null;
    this.imageSrc = 'https://img2.baidu.com/it/u=2048195462,703560066&fm=253&app=138&size=w931&n=0&f=JPEG&fmt=auto?sec=1697216400&t=af53de15fb5e0c74bdb55ed808562741'
    this.widget = this.addWidget("button", "上传图片", '', function (value, widget, node) {
        const imageUpload = document.createElement('input');
        imageUpload.type = "file"
        imageUpload.accept = "image/*"
        imageUpload.addEventListener('change', uploadImage);

        function uploadImage(event) {
            const file = imageUpload.files[0];
            const reader = new FileReader();

            reader.onload = function (event) {
                that.imageSrc = event.target.result
            };
            reader.readAsDataURL(file);
        }
        imageUpload.click();
    });
    this.size = [200, 230]
}

//name to show
CustomImageInputNode.title = "上传图片";

//function to call when the node is executed
CustomImageInputNode.prototype.onExecute = function () {

}

CustomImageInputNode.prototype.onDrawForeground = function (ctx, graphcanvas) {
    if (this.flags.collapsed) return;

    const image = document.createElement("img") //new Image()
    image.src = this.imageSrc;

    ctx.save();
    ctx.fillColor = "black";
    ctx.drawImage(image, 0, 60, this.size[0], this.size[1] - 60)
    ctx.restore();
}

CustomImageInputNode.prototype.onMouseDown = function (event, pos, graphcanvas) {

}

// myClass = [{ type: , nodeClass: CustomImageInputNode, }]
CustomImageInputNode.type = 'Input/Image'

export default CustomImageInputNode