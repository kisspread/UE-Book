# Android Camera Player

> Implements camera preview using the Android Camera library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓相机播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidCamera` (Runtime), `AndroidCameraEditor` (Editor), `AndroidCameraFactory` (Runtime, Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera) | |

## 总体用途

Android Camera Player 是 Unreal Engine 媒体框架的一个 Android 平台插件，利用 Android 原生 Camera API 实现实时相机预览功能。它将 Android 设备的前/后摄像头捕捉的画面作为媒体源，通过标准的 `UMediaPlayer` 和 `UMediaTexture` 管道进行播放，支持在 3D 场景中显示实时相机画面、录像或照片拍摄。该插件解决了在 UE 应用中集成 Android 相机功能的需求，提供与平台无关的媒体玩家接口，使开发者能以处理普通视频流的方式控制相机预览。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `AndroidCamera` | Runtime | 核心运行时代码，封装 Android Camera 生命周期、帧缓冲管理和 JNI 调用，驱动相机预览播放器。 |
| `AndroidCameraEditor` | Editor | 编辑器模块，提供 Android 相机设备相关的设置面板或属性自定义（如默认相机方向、分辨率等）。 |
| `AndroidCameraFactory` | Runtime / Editor | 工厂模块，负责创建 `UMediaPlayer` 使用的 `IMediaPlayer` 实例，支持在编辑器和运行时中生成相机媒体玩家。 |

## 使用场景

- **AR 应用**：在 AR 场景中实时显示真实世界相机画面作为背景。
- **视频录制/拍照**：通过媒体框架配合 `MediaCapture` 实现录像或抓图功能。
- **Android 相机预览**：在 UI 或 3D 场景中嵌入实时相机预览，可用于扫码、人脸识别、远程协助等。
- **跨平台媒体播放**：统一使用 `MediaPlayer` 控制相机，与其他视频源切换播放。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Media/MediaAssets 等）。

> 详细依赖请参见各模块文档。

## 维护状态

### 近期更新

| 日期 | 哈希 | 修改说明 |
|---|---|---|
| 2025-09-11 | `6312e16d` | 修复非 Shipping 构建中因 JNI 异常导致的崩溃 |
| 2025-08-29 | `32884de4` | 将 `RHICreateTexture` 改为 `RHICmdList.CreateTexture` |
| 2025-08-12 | `f5866ce3` | 修复 `AndroidCameraPlayer` 中 `MediaOpened` 事件的触发时机 |
| 2025-08-08 | `d7c83195` | 修复 `CameraDevice` 初始化过程中关闭设备时的 Java 异常 |
| 2025-06-26 | `9294da93` | 移除两个未使用的导入 |

### 维护评价

该插件创建于 2025 年 6 月，属于较新的组件。近期更新集中在 JNI 异常修复、渲染接口更替以及事件时序优化，表明团队正在持续提升稳定性与 API 兼容性。开发活跃，推荐在 Android 平台上使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera)
- [官方论坛帖（媒体框架文档）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AndroidCamera/Source)（无独立测试目录，请参见源码）