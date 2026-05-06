# Image Sequence Media Player

> Implements a media player for image sequences in EXR and other formats.

| 属性 | 值 |
|---|---|
| 中文名 | 图像序列媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ExrReaderGpu` (Runtime), `ImgMedia` (Runtime), `ImgMediaEditor` (Runtime), `ImgMediaEngine` (Runtime), `ImgMediaFactory` (Runtime), `OpenExrWrapper` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia) | |

---

## 总体用途

**ImgMedia** 插件是 Unreal Engine 中用于播放图像序列（Image Sequence）的媒体播放器实现。它支持 **EXR** 等常见图像格式，允许将连续帧序列作为视频媒体源进行加载、播放和 scrubbing。

**解决的核心问题**：UE 原生媒体播放器（如 File Media Source）仅支持传统视频容器（如 mp4、mov），无法直接使用序列帧作为输入。此插件通过封装 OpenEXR 库并提供 GPU 加速读取，实现高效、可随机访问的序列帧播放，适用于需要高动态范围（HDR）或未压缩序列帧的高品质项目（如电影级过场、虚拟制片监控等）。

---

## 模块列表

| 模块 | 一句话说明 | 详细文档 |
|---|---|---|
| `ExrReaderGpu` (Runtime) | GPU 加速的 EXR 帧读取器，利用 OpenEXR 库直接在显存中解码。 | [ExrReaderGpu.md](ExrReaderGpu.md) |
| `ImgMedia` (Runtime) | 核心媒体播放器逻辑，包括播放器、轨道、帧缓存管理。 | [ImgMedia.md](ImgMedia.md) |
| `ImgMediaEditor` (Runtime) | 编辑器支持，提供导入选项、设置界面等。 | [ImgMediaEditor.md](ImgMediaEditor.md) |
| `ImgMediaEngine` (Runtime) | 与引擎集成部分，包括媒体源适配、Actor/Component 绑定。 | [ImgMediaEngine.md](ImgMediaEngine.md) |
| `ImgMediaFactory` (Runtime) | 工厂模块，负责创建 `IMediaPlayer` 实例并注册到媒体框架。 | [ImgMediaFactory.md](ImgMediaFactory.md) |
| `OpenExrWrapper` (Runtime) | 对 OpenEXR 开源库的 C++ 封装层，供其他模块使用。 | [OpenExrWrapper.md](OpenExrWrapper.md) |

---

## 使用场景

- **高品质过场动画**：需要使用逐帧 EXR 序列代替压缩视频以保留完整动态范围与细节。
- **虚拟制片 & 实时合成**：使用图像序列作为背景或元素进行实时合成，支持随意跳转帧（scrubbing）而不重压。
- **科研 / 医疗可视化**：播放通过专业相机或模拟器生成的序列帧（如 OpenEXR 16bit float 深度图）。
- **批量资产预览**：在编辑器中快速预览大量序列帧资源，查看帧内容。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ImgMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- 测试用例：`Engine/Source/Programs/AutomationTests/Tests/Media/ImgMedia/`（若有）