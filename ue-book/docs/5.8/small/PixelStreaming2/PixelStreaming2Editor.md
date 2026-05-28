# Pixel Streaming 2

> Streaming of Unreal Engine audio and rendering to WebRTC-compatible media players such as a web browsers.

| 属性 | 值 |
|---|---|
| 中文名 | 像素流2 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PixelStreaming2` (Runtime), `PixelStreaming2Core` (Runtime), `PixelStreaming2Editor` (Runtime), `PixelStreaming2HMD` (Runtime), `PixelStreaming2Input` (Runtime), `PixelStreaming2RTC` (Runtime), `PixelStreaming2Servers` (Runtime), `PixelStreaming2Settings` (Runtime), `EpicRtc` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2) | |

## 用途

Pixel Streaming 2 是 Epic 为 UE5 全新重写的像素流方案，替代旧版 Pixel Streaming 插件。它允许将 Unreal Engine 的渲染画面和音频通过 WebRTC 协议实时传输到任何兼容 WebRTC 的播放器（如浏览器），无需用户在本地安装任何客户端软件。

与第一代 Pixel Streaming 相比，Pixel Streaming 2 具有以下核心改进：

- **模块化架构**：将功能拆分为独立模块（Core、RTC、Input、Servers、HMD、Editor 等），便于维护和扩展
- **EpicRtc**：使用 Epic 自研的 WebRTC 实现，不再依赖第三方 libwebrtc 编译，简化了构建流程
- **编辑器流送**：支持在编辑器中直接启动流送，可将整个编辑器窗口或场景视口实时传输到浏览器，适用于远程演示和评审
- **内建信令服务器**：内置 C++ 信令服务器，无需外部 Node.js 进程即可工作

## 使用场景

- 云游戏服务 → 将游戏画面通过 WebRTC 流送到玩家浏览器
- 远程编辑器访问 → 通过浏览器远程访问 UE 编辑器，进行场景编辑和评审
- 建筑/汽车可视化 → 客户端无需安装 UE，通过浏览器即可体验高保真 3D 内容
- VP8/VP9/H264/AV1 编码 → 选择合适的编码器适配不同网络环境和终端设备
- HMD 流送 → 将 VR 内容流送到浏览器端的 VR 体验

## 模块架构

| 模块 | 用途 |
|---|---|
| `PixelStreaming2` | 主模块，负责流送管线与 VulkanRHI 集成 |
| `PixelStreaming2Core` | 核心接口与类型定义 |
| `PixelStreaming2Editor` | 编辑器专用流送功能、工具栏 UI |
| `PixelStreaming2HMD` | VR/HMD 流送支持 |
| `PixelStreaming2Input` | 远程输入处理（鼠标、键盘、触摸、手柄） |
| `PixelStreaming2RTC` | WebRTC 传输层（编解码、网络传输） |
| `PixelStreaming2Servers` | 内建信令服务器和 Web 服务器 |
| `PixelStreaming2Settings` | 插件设置项（运行时配置） |
| `EpicRtc` | Epic 自研 WebRTC 实现（第三方） |

## 蓝图用法

本模块（PixelStreaming2Editor）主要面向编辑器扩展，不直接暴露蓝图节点。流送的核心蓝图 API 由 `PixelStreaming2Core` 和 `PixelStreaming2` 主模块提供。

### 编辑器工具栏

PixelStreaming2Editor 在编辑器工具栏注入了专用 UI 菜单，支持以下操作：

| 操作 | 说明 |
|---|---|
| 启动/停止信令服务器 | 控制内建 C++ 信令服务器的启停 |
| 启动/停止流送 | 将编辑器画面流送到浏览器 |
| 流送模式切换 | 全编辑器窗口 / 仅关卡编辑器视口 |
| 编解码器选择 | VP8 / VP9 / H264 / AV1 |
| HTTPS 配置 | 设置 SSL 证书路径，启用 HTTPS 前端服务 |
| 外部/内建信令切换 | 选择使用内建或外部信令服务器 |

### 资产创建

编辑器提供了以下工厂类，可通过内容浏览器右键菜单创建资产：

| 工厂类 | 创建的资产 |
|---|---|
| `UPixelStreaming2MediaTextureFactory` | Pixel Streaming 2 Media Texture |
| `UPixelStreaming2VideoProducerBackBufferFactory` | 视频生产者（后缓冲合成） |
| `UPixelStreaming2VideoProducerMediaCaptureFactory` | 视频生产者（媒体捕获） |
| `UPixelStreaming2VideoProducerRenderTargetFactory` | 视频生产者（渲染目标） |

## C++ 用法

### 头文件引入

```cpp
#include "IPixelStreaming2EditorModule.h"
```

### 基本用法

```cpp
// 检查模块是否可用
if (IPixelStreaming2EditorModule::IsAvailable())
{
    // 获取模块实例
    IPixelStreaming2EditorModule& EditorModule = IPixelStreaming2EditorModule::Get();
    
    // 启动编辑器流送（流送整个编辑器窗口）
    EditorModule.StartStreaming(EPixelStreaming2EditorStreamTypes::Editor);
    
    // 或仅流送关卡编辑器视口
    // EditorModule.StartStreaming(EPixelStreaming2EditorStreamTypes::LevelEditor);
}
```

### 信令服务器配置

```cpp
// 获取编辑器模块
IPixelStreaming2EditorModule& EditorModule = IPixelStreaming2EditorModule::Get();

// 配置信令域名
EditorModule.SetSignallingDomain(TEXT("ws://127.0.0.1"));

// 配置端口
EditorModule.SetStreamerPort(8888);   // 流送器连接端口
EditorModule.SetViewerPort(8080);     // 浏览器查看端口

// 启用 HTTPS（需要证书）
EditorModule.SetServeHttps(true);
EditorModule.SetSSLCertificatePath(TEXT("/path/to/cert.pem"));
EditorModule.SetSSLPrivateKeyPath(TEXT("/path/to/key.pem"));

// 启动内建信令服务器
EditorModule.StartSignalling();

// 获取信令服务器实例（可用于更细粒度的控制）
TSharedPtr<UE::PixelStreaming2Servers::IServer> Server = EditorModule.GetSignallingServer();

// 启动流送
EditorModule.StartStreaming(EPixelStreaming2EditorStreamTypes::Editor);

// 停止
EditorModule.StopStreaming();
EditorModule.StopSignalling(/*bForce=*/true);
```

### 进阶用法：自定义视频生产者

编辑器模块提供了三种视频生产者实现，可根据需要选择：

```cpp
#include "VideoProducerBackBufferComposited.h"  // 整个编辑器窗口合成
#include "VideoProducerLevelEditor.h"            // 关卡编辑器视口

// 创建后缓冲合成视频生产者（包含所有窗口和覆盖层）
auto BackBufferProducer = FVideoProducerBackBufferComposited::Create();

// 监听帧尺寸变化
BackBufferProducer->OnFrameSizeChanged.AddLambda([](TWeakPtr<FIntRect> Rect) {
    // 处理尺寸变化
});

// 创建关卡编辑器视口视频生产者（仅主场景视口）
auto LevelEditorProducer = FVideoProducerLevelEditor::Create();
```

## 模块依赖

`PixelStreaming2Editor` 的 Build.cs 依赖：

| 模块 | 用途 |
|---|---|
| `PixelStreaming2Core` | 核心接口与类型 |
| `PixelStreaming2RTC` | WebRTC 流送器接口 |
| `PixelStreaming2Servers` | 内建信令服务器接口 |
| `PixelStreaming2Settings` | 插件设置访问 |
| `PixelStreaming2Input` | 输入处理（仅 Private 依赖） |
| `VulkanRHI` | Vulkan 渲染后端支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `c1dab3e1` | [PixelStreaming2] Fix: Input handler obtaining default target window from wrong method | 修复输入处理器从错误方法获取默认目标窗口的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 虚拟制片：将 VP 资产迁移至新的资产分类目录 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 UE::FSharedString |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出乱码 |

### 维护评价

**活跃维护**

- **创建时间**：2024-09-04，约 2 年前创建，属于较新的插件
- **更新频率**：近期保持稳定的更新节奏（2026 年 4-5 月有多次提交），涵盖 bug 修复、编译警告清理和资产分类调整
- **维护状态**：作为 Epic Games 官方维护的插件，处于持续活跃开发中，是 Pixel Streaming 第一代的正式继任者
- **注意**：`EnabledByDefault=false`，需在项目设置中手动启用
- **推荐使用**：推荐。这是 Epic 官方推荐的新一代像素流方案，架构更现代，模块化程度高，适合新项目采用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2)
- [官方文档](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/PixelStreaming2/Tests)（如有）