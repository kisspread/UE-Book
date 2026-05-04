# Epic Stage App

> Enables remote connections from the Epic Stage App

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | 未知 |
| 包含内容 | true |
| 模块 | EpicStageApp (Runtime) |
| 创建时间 | 2022-06-08 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/EpicStageApp) | |

## 用途

EpicStageApp 是 Epic Games 为其 **Unreal Stage App**（移动端/平板端应用）提供的 UE5 服务端插件。它为 Stage App 提供了与 Unreal Engine 实例之间的远程通信能力，核心功能包括：

1. **设备发现（Discovery）**：通过 UDP 多播 beacon 协议，让 Stage App 在局域网内自动发现运行中的 Unreal Engine 实例。引擎启动后会监听指定的多播地址和端口，响应 beacon 消息并返回 WebSocket 端口和引擎友好名称。
2. **nDisplay 预览渲染**：通过 WebSocket 路由，Stage App 可以请求引擎渲染 nDisplay 集群的预览画面（支持透视、方位角、正交、UV 四种投影模式），并将渲染结果以 JPEG 格式返回。
3. **远程 Light Card / Stage Actor 操控**：Stage App 可以在预览画面上拖拽、创建、复制 Light Card 等 Stage Actor，实现远程编辑 nDisplay 场景中的灯光卡、旗板等虚拟制作元素。
4. **客户端绑定对象管理**：支持创建生命周期与 WebSocket 客户端连接绑定的对象。

本质上，这个插件是 Unreal Engine 与 Epic Stage App 移动端之间的 **WebSocket 桥接层**，让现场虚拟制作团队可以通过 iPad 等设备远程操控引擎中的 nDisplay 配置。

## 使用场景

- 你在使用 **nDisplay** 进行虚拟制作（LED Volume / ICVFX），需要在现场通过 iPad 远程调整 Light Card 位置和参数
- 你需要在局域网内通过 **Epic Stage App** 自动发现并连接到运行中的 Unreal Engine 实例
- 你需要远程请求 nDisplay 场景的预览渲染（俯视图/方位角投影），用于虚拟制作的实时监控
- 你需要通过移动端应用远程创建、拖拽、复制 nDisplay 场景中的 Light Card 和 Flag

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAPIVersion` | 获取 Stage App API 的语义版本号字符串（如 "1.10.0"） | `UStageAppFunctionLibrary` |
| `GetRemoteControlWebInterfacePort` | 获取 Remote Control Web 接口的端口号 | `UStageAppFunctionLibrary` |

### 使用示例（蓝图描述）

这两个函数都是 `BlueprintPure`（无副作用），可以在任意蓝图中调用：

1. **获取 API 版本**：拖入 `GetAPIVersion` 节点，输出连接到 Print String 或 UI Text，用于显示当前引擎支持的 Stage App API 版本。
2. **获取 Web 接口端口**：拖入 `GetRemoteControlWebInterfacePort` 节点，可用于在 UI 上显示 Remote Control Web 界面的访问地址。

## C++ 用法

### 头文件引入

```cpp
#include "StageAppLibrary.h"
#include "StageAppVersion.h"
#include "StageAppSettings.h"
```

### 基本用法

```cpp
// 获取 Stage App API 版本
FString Version = UStageAppFunctionLibrary::GetAPIVersion();
// 返回格式: "1.10.0"

// 获取 Remote Control Web 接口端口
int32 Port = UStageAppFunctionLibrary::GetRemoteControlWebInterfacePort();

// 直接访问版本号组件
uint16 Major = FEpicStageAppAPIVersion::Major;  // 1
uint16 Minor = FEpicStageAppAPIVersion::Minor;  // 10
uint16 Patch = FEpicStageAppAPIVersion::Patch;  // 0
```

### 配置项

Stage App 的发现设置位于 **Project Settings → Plugins → Epic Stage App**：

```cpp
// 获取 Stage App 配置
const UStageAppSettings& Settings = *GetDefault<UStageAppSettings>();

// UDP 多播发现地址（默认: "230.0.0.2"）
FString Endpoint = Settings.DiscoveryEndpoint;

// UDP 多播发现端口（默认: 6667）
int32 Port = Settings.DiscoveryPort;
```

这些设置存储在 `Engine.ini` 中，可以通过编辑器的 Project Settings 面板修改。

### 命令行参数

引擎启动时可通过以下命令行参数自定义 Stage App 行为：

- `-StageFriendlyName=<名称>` — 设置引擎实例在 Stage App 中显示的友好名称
- `-CONCERTDISPLAYNAME=<名称>` — 备选名称参数（兼容 Multi-User 编辑的命名约定）

如果没有指定这些参数，默认使用 `FApp::GetSessionOwner()` 作为显示名称。

## WebSocket 路由协议

EpicStageApp 注册了以下 WebSocket 路由，供 Stage App 客户端调用：

### nDisplay 预览渲染路由

| 路由 | 说明 |
|---|---|
| `ndisplay.preview.renderer.create` | 创建 nDisplay 预览渲染器 |
| `ndisplay.preview.renderer.setroot` | 设置渲染器的根 DisplayCluster Actor |
| `ndisplay.preview.renderer.configure` | 修改渲染器配置（分辨率、投影类型、FOV 等） |
| `ndisplay.preview.renderer.destroy` | 销毁预览渲染器 |
| `ndisplay.preview.render` | 请求渲染一帧预览画面（返回 Base64 JPEG） |

### Actor 操控路由

| 路由 | 说明 |
|---|---|
| `ndisplay.preview.actor.drag.begin` | 开始拖拽 Actor |
| `ndisplay.preview.actor.drag.move` | 移动正在拖拽的 Actor |
| `ndisplay.preview.actor.drag.end` | 结束拖拽 Actor |
| `ndisplay.preview.actor.create` | 在预览视口中创建 Actor（Light Card） |
| `stageapp.actors.duplicate` | 复制已有 Actor |

### 客户端对象路由

| 路由 | 说明 |
|---|---|
| `stageapp.clientobject.create` | 创建与客户端连接绑定的对象 |
| `stageapp.clientobject.destroy` | 销毁客户端绑定对象 |

### 服务端事件

引擎会向客户端推送以下事件：

| 事件类型 | 说明 |
|---|---|
| `PreviewRendererCreated` | 渲染器创建完成，返回 RendererId |
| `PreviewRenderCompleted` | 预览渲染完成，包含 Base64 JPEG 图像和 Actor 投影位置 |
| `ActorDragCancelled` | 拖拽操作被引擎取消（超时） |
| `RequestedActorsCreated` | 请求创建的 Actor 已完成 |
| `RequestedClientObjectCreated` | 请求创建的客户端对象已完成 |

### 预览渲染器设置

创建或配置渲染器时可指定以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `RenderType` | Enum | Color | 渲染类型（Color / Normals） |
| `ProjectionType` | Enum | Azimuthal | 投影类型（Perspective / Azimuthal / Orthographic / UV） |
| `Resolution` | IntPoint | 1024×1024 | 渲染分辨率 |
| `FOV` | float | 130.0 | 水平和垂直视场角（度） |
| `Rotation` | Rotator | (90,0,0) | 预览相机相对旋转 |
| `JpegQuality` | int | 50 | JPEG 压缩质量（50-100） |
| `IncludeActorPositions` | bool | false | 是否在渲染结果中包含 Actor 投影坐标 |

## Demo 示例

本插件主要作为 **服务端运行时模块** 使用，不提供可直接调用的 Gameplay API。其典型集成方式是：

1. 启用 EpicStageApp 插件（及其依赖的 RemoteControl、nDisplay、DiscoveryBeaconReceiver）
2. 确保 Remote Control WebSocket 服务器正在运行（Project Settings → Remote Control）
3. 在同一局域网内使用 Epic Stage App 连接

### Build.cs 依赖

```csharp
// 如果你的模块需要引用 EpicStageApp 的公共类型
PublicDependencyModuleNames.Add("EpicStageApp");
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取（即使用者需要的依赖）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Serialization` | 序列化支持 |

插件自身的私有依赖（不需要使用者直接引用）：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | Remote Control 框架，提供 WebSocket 通信基础设施 |
| `WebRemoteControl` | Remote Control 的 WebSocket 服务器实现 |
| `RemoteControlCommon` | Remote Control 公共类型 |
| `DisplayCluster` | nDisplay 核心模块 |
| `DisplayClusterScenePreview` | nDisplay 场景预览渲染 |
| `DisplayClusterLightCardExtender` | Light Card 扩展功能 |
| `DisplayClusterLightCardEditorShaders` | Light Card 编辑器着色器 |
| `DiscoveryBeaconReceiver` | UDP 多播设备发现框架 |
| `Networking` / `Sockets` | 网络通信 |
| `ImageWrapper` | 图像编码（JPEG 压缩） |
| `RHI` | 渲染硬件接口 |
| `DeveloperSettings` | 开发者设置框架 |
| `Engine` | 引擎核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-12 | `ce6ff39` | 修复 `FTSTicker::RemoveTicker` 的 `nodiscard` 警告 | 编译警告修复，非功能性更新 |
| 2025-01-28 | `ff02637` | nDisplay HoldoutComposite 集成 3/3：将 nDisplay 预览与 HoldoutComposite 插件集成 | 功能性更新：支持 HoldoutComposite 渲染 |
| 2024-09-11 | `f1c52f2` | [UnrealStage] API 版本升级至 1.10.0，适配 UE 5.5 新功能 | API 版本更新 |

### 维护评价

- **创建时间**：2022-06-08，约 4 年前
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，仍处于 Beta 阶段
- **平台限制**：仅支持 Win64 和 Linux
- **活跃度**：2025 年仍有功能性更新（HoldoutComposite 集成），维护较活跃
- **依赖链复杂**：深度依赖 nDisplay 和 Remote Control 生态，不是独立使用的插件
- **推荐使用**：如果你在做虚拟制作 / ICVFX 且需要使用 Epic Stage App，这是必需插件。对于普通游戏开发项目，不需要启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/EpicStageApp)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[RemoteControl](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)、[nDisplay](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/nDisplay)
