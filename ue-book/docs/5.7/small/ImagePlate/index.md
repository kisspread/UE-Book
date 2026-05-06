# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图片板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate) | |

## 用途

Image Plate 提供一种始终朝向摄像机的图片板（类似公告板），可用于快速展示 2D 图像、序列帧或材质。常用于电影级视效预览、虚拟制片中的参考背景、以及低成本的 2D 元素嵌入。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `ImagePlate` | Runtime | 核心运行时：定义 `AImagePlate` Actor 和 `UImagePlateComponent`，支持图片序列、纹理、材质绑定 |
| `ImagePlateEditor` | Editor | 编辑器集成：提供图片板编辑工具、材质/纹理选择 UI、以及蓝图节点支持 |

详细 API 请参考各模块文档：
- [ImagePlate 模块](./ImagePlate.md)
- [ImagePlateEditor 模块](./ImagePlateEditor.md)

## 使用场景

- **虚拟制片**：在绿幕合成中放置参考背景图片，保持始终面向摄像机
- **UI 原型**：在 3D 场景中快速显示 Logo 或静态图片，无需制作 3D 模型
- **电影预可视化**：使用序列帧模拟动态背景或特效
- **2D 元素嵌入**：在 3D 世界中展示 2D 文字、图标或图片公告板

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/image-plate-plugin/)（若有）
- [测试用例（暂无明确测试路径）]（插件文件较少，测试可能在 `Engine/Tests` 中）