# Apple Image Utils

> Utilities that operate on CIImage, CVPixelBuffer, IOSurface, etc.

| 属性 | 值 |
|---|---|
| 中文名 | 苹果图像工具 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleImageUtils` (Runtime), `AppleImageUtilsBlueprintSupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils) | |

## 用途

为 Unreal Engine 提供与 Apple 平台原生图像格式（CIImage、CVPixelBuffer、IOSurface）之间的桥接能力。运行时模块专供 LiveLinkHub 使用，蓝图支持模块则在 Win64/Mac/Linux 开发环境下提供蓝图可调用的图像转换工具函数。主要用于需要在 UE 与 Apple 原生图像管线之间传递图像数据的场景，例如与 macOS/iOS 摄像头或视频采集设备集成。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`AppleImageUtils`](AppleImageUtils.md) | Runtime | Apple 原生图像格式（CIImage/CVPixelBuffer/IOSurface）转换核心逻辑，限 LiveLinkHub 使用 |
| [`AppleImageUtilsBlueprintSupport`](AppleImageUtilsBlueprintSupport.md) | UncookedOnly | 蓝图可调用的图像转换节点，支持 Win64/Mac/Linux 编辑器环境 |

## 使用场景

- 你在开发涉及 Apple 设备摄像头或视频采集的实时应用 → 用此插件桥接 CVPixelBuffer/IOSurface 与 UE 纹理
- 你使用 LiveLinkHub 从 macOS/iOS 设备传入图像流 → 运行时模块提供底层转换支持
- 你需要在蓝图中将 CIImage 转换为 UE 可用纹理 → 使用蓝图支持模块中的转换节点

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils)
- [AppleImageUtils 模块文档](AppleImageUtils.md)
- [AppleImageUtilsBlueprintSupport 模块文档](AppleImageUtilsBlueprintSupport.md)