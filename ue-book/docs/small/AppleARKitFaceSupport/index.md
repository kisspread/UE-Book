# Apple ARKit Face Support

> Support for Apple's face tracking features

| 属性 | 值 |
|---|---|
| 分类 | Augmented Reality |
| 默认启用 | ❌ 否（`EnabledByDefault: false`） |
| 包含内容 | 是 |
| 模块 | AppleARKitFaceSupport (Runtime, PostConfigInit) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董（约 5.6 年） |
| 支持平台 | iOS, Win64, Mac, Linux, Android |
| 依赖插件 | AppleARKit, ProceduralMeshComponent, AppleImageUtils |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport) | |

## 用途

AppleARKitFaceSupport 是 UE5 中 Apple ARKit 面部追踪功能的核心支撑插件。它解决了三个关键问题：

1. **面部网格渲染**：通过 `UAppleARKitFaceMeshComponent`（继承自 `UProceduralMeshComponent`）将 ARKit 追踪到的 52 个面部混合形状（Blend Shape）实时转化为可渲染的 3D 面部网格。支持从 ARKit 原生顶点数据构建网格，也支持仅通过混合形状参数动态生成。

2. **LiveLink 面部数据传输**：将 iOS 设备上 ARKit 采集的面部混合形状数据通过 LiveLink 管线发布，供桌面端（PC/Mac）的动画系统消费。支持：
   - 本地 LiveLink 直连（iOS 端直接发布）
   - UDP 远程传输（iOS → 桌面端，通过 socket 跨设备发送）
   - 本地文件录制（CSV/JSON 格式保存面部动画数据）

3. **网络复制**：支持面部混合形状数据的多人游戏网络同步——客户端采集面部数据后通过 `ServerUpdateFaceCurves` RPC 发送到服务器，再复制到其他客户端。

## 使用场景

- **iOS 面部捕捉 → UE5 动画**：在 iPhone/iPad 上使用 TrueDepth 摄像头捕捉演员面部表情，通过 LiveLink 实时驱动 UE5 中的 MetaHuman 或自定义角色面部动画。
- **多人游戏中的面部表情同步**：在多人网络游戏中，将玩家的实时面部表情通过网络复制同步到其他玩家的客户端，用于社交 VR 或虚拟直播。
- **面部动画录制与回放**：通过内置的文件写入功能将面部动画数据录制为 CSV/JSON 文件，后续可以离线回放或导入到动画工具中。
- **桌面端远程接收**：在 PC 上通过 UDP socket 监听来自 iOS 设备的面部数据流，无需 iOS 设备直连 UE 编辑器。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Face Mesh` | 从顶点、三角形、UV 数据创建面部网格 | `UAppleARKitFaceMeshComponent` |
| `Create Face Mesh from Blend Shapes` | 设置一组混合形状值 | `UAppleARKitFaceMeshComponent` |
| `Set the value of a Blend Shape` | 设置单个混合形状的值（0..1） | `UAppleARKitFaceMeshComponent` |
| `Get Face Blend Shape Amount` | 获取指定混合形状的当前值 | `UAppleARKitFaceMeshComponent` |
| `Update Face Mesh from Blend Shapes` | 根据当前混合形状重新生成网格 | `UAppleARKitFaceMeshComponent` |
| `Update Mesh Section` | 仅更新网格顶点位置 | `UAppleARKitFaceMeshComponent` |
| `Modify auto bind to local face tracking` | 开启/关闭自动绑定本地面部追踪 | `UAppleARKitFaceMeshComponent` |
| `Publish Via Live Link` | 将面部数据通过 LiveLink 发布 | `UAppleARKitFaceMeshComponent` |
| `Get Transform` | 获取 AR 摄像头检测到的面部变换 | `UAppleARKitFaceMeshComponent` |
| `Get Last Update Frame Number` | 获取最后更新的帧号 | `UAppleARKitFaceMeshComponent` |
| `Get Last Update Timestamp` | 获取最后更新的时间戳 | `UAppleARKitFaceMeshComponent` |

### 组件属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `bWantsMeshUpdates` | bool | 是否构建渲染用网格数据 |
| `bWantsCollision` | bool | 是否为面部网格创建碰撞（有性能开销） |
| `bAutoBindToLocalFaceMesh` | bool | 是否自动从本地 ARKit 追踪数据更新（每 Tick） |
| `TransformSetting` | EARFaceComponentTransformMixing | 组件变换与追踪变换的混合方式 |
| `bFlipTrackedRotation` | bool | 是否翻转追踪旋转（-X 方向朝外 vs +X） |
| `FaceMaterial` | UMaterialInterface | 面部网格渲染材质 |
| `LiveLinkSubjectName` | FName | LiveLink 主题名称 |

### 变换混合模式（EARFaceComponentTransformMixing）

| 模式 | 说明 |
|---|---|
| `ComponentOnly` | 仅使用组件变换（非追踪网格时使用） |
| `ComponentLocationTrackedRotation` | 使用组件位置 + 追踪旋转 |
| `ComponentWithTracked` | 组件变换与追踪变换串联 |
| `TrackingOnly` | 仅使用追踪变换 |

### 使用示例（蓝图描述）

**自动绑定面部追踪（最简方案）：**
1. 在 Actor 上添加 `AppleARKitFaceMeshComponent`
2. 设置 `bAutoBindToLocalFaceMesh = true`
3. 设置 `bWantsMeshUpdates = true`
4. 设置 `FaceMaterial` 为你的面部材质
5. 组件会自动在每帧从 ARKit 追踪数据更新网格和混合形状

**通过 LiveLink 发布面部数据：**
1. 添加 `AppleARKitFaceMeshComponent` 到 Actor
2. 调用 `Publish Via Live Link` 节点，传入 Subject Name（如 "FaceAR"）
3. 在 LiveLink 面板中可以看到新的 ARKit 源

## C++ 用法

### 头文件引入

```cpp
#include "AppleARKitFaceMeshComponent.h"
#include "AppleARKitLiveLinkSourceFactory.h"
```

### 基本用法 — 获取混合形状值

```cpp
// 获取面部网格组件
UAppleARKitFaceMeshComponent* FaceMeshComp = /* ... */;

// 读取当前混合形状值
float JawOpen = FaceMeshComp->GetFaceBlendShapeAmount(EARFaceBlendShape::JawOpen);
float SmileLeft = FaceMeshComp->GetFaceBlendShapeAmount(EARFaceBlendShape::MouthSmileLeft);

// 手动设置混合形状
FaceMeshComp->SetBlendShapeAmount(EARFaceBlendShape::EyeBlinkLeft, 1.0f);
```

来源：`AppleARKitFaceMeshComponent.h`（Public 接口）

### 基本用法 — LiveLink 发布

```cpp
// 方式一：通过组件发布
UAppleARKitFaceMeshComponent* FaceMeshComp = /* ... */;
FaceMeshComp->PublishViaLiveLink(FName("MyFaceSubject"));

// 方式二：通过工厂直接创建 LiveLink 源（iOS 端直连）
TSharedPtr<ILiveLinkSourceARKit> Source = FAppleARKitLiveLinkSourceFactory::CreateLiveLinkSource();

// 方式三：创建远程监听源（桌面端接收来自 iOS 的 UDP 数据）
FAppleARKitLiveLinkConnectionSettings Settings;
Settings.Port = 11111;
TSharedPtr<ILiveLinkSourceARKit> RemoteSource = FAppleARKitLiveLinkSourceFactory::CreateLiveLinkSource(Settings);
```

来源：`AppleARKitLiveLinkSourceFactory.h`、`AppleARKitFaceSupportImpl.cpp`

### 进阶用法 — 远程 UDP 发布与文件录制

```cpp
// iOS 端：创建远程发布器，通过 UDP 发送到指定 IP
TSharedPtr<IARKitBlendShapePublisher> RemotePub =
    FAppleARKitLiveLinkSourceFactory::CreateLiveLinkRemotePublisher(TEXT("192.168.1.100"));

// iOS 端：创建本地文件写入器（通过项目设置 AppleARKitSettings 的 FaceTrackingFileWriterType 配置）
TSharedPtr<IARKitBlendShapePublisher> FileWriter =
    FAppleARKitLiveLinkSourceFactory::CreateLiveLinkLocalFileWriter();

// 手动发布混合形状数据
if (RemotePub.IsValid())
{
    RemotePub->PublishBlendShapes(SubjectName, FrameTime, BlendShapes, DeviceID);
}
```

来源：`AppleARKitLiveLinkSourceFactory.h`、`AppleARKitLiveLinkSource.cpp`

### 进阶用法 — 控制台命令

```cpp
// 运行时通过控制台命令设置远程 LiveLink 发送目标
// 控制台命令: LiveLinkFaceAR SendTo=192.168.1.100
```

来源：`AppleARKitFaceSupportImpl.cpp` 中的 `Exec_Runtime`

## Demo 示例

### 最小化面部追踪组件

```cpp
// MyFaceActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyFaceActor.generated.h"

UCLASS()
class AMyFaceActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFaceActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<class UAppleARKitFaceMeshComponent> FaceMeshComponent;
};

// MyFaceActor.cpp
#include "MyFaceActor.h"
#include "AppleARKitFaceMeshComponent.h"

AMyFaceActor::AMyFaceActor()
{
    FaceMeshComponent = CreateDefaultSubobject<UAppleARKitFaceMeshComponent>(TEXT("FaceMesh"));
    FaceMeshComponent->bAutoBindToLocalFaceMesh = true;
    FaceMeshComponent->bWantsMeshUpdates = true;
    FaceMeshComponent->bFlipTrackedRotation = true;
    RootComponent = FaceMeshComponent;
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "AppleARKitFaceSupport"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎模块 |
| `Engine` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `HeadMountedDisplay` | XR/HMD 基础设施 |
| `XRBase` | XR 基础接口 |
| `AugmentedReality` | UE5 AR 抽象层（`UARFaceGeometry`、`EARFaceBlendShape` 等） |
| `ProceduralMeshComponent` | 动态网格构建（面部网格渲染基础） |
| `LiveLinkInterface` | LiveLink 框架接口 |
| `Sockets` | UDP socket 通信（远程数据传输） |
| `AppleARKit` | Apple ARKit 底层集成 |
| `AppleImageUtils` | Apple 图像处理工具 |
| `Slate` / `SlateCore` / `PropertyEditor` | 编辑器 UI（仅编辑器构建） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-11 | `8406cd44` | Replace some usages of FORCEINLINE with inline in AR modules | 代码规范清理，将部分 `FORCEINLINE` 替换为 `inline`，无功能变更 |
| 2024-10-07 | `a8971688` | Set a min / max value for ARKit connection settings | 为 LiveLink 连接端口添加 `ClampMin=1, ClampMax=32765` 限制 |
| 2024-04-17 | `a1d5ecfc` | Fix ios compile error | 修复 iOS 编译错误 |

### 维护评价

- **创建时间**：2020 年 9 月，随 UE5 早期版本引入，已有约 5.6 年历史
- **更新频率**：最近 3 次更新跨越约 14 个月，均为小修（编译修复、代码清理、参数校验），没有功能性更新
- **功能稳定性**：插件功能已相当成熟和完善，52 个 Blend Shape 的映射、LiveLink 集成、UDP 传输、网络复制等核心功能均在早期版本中完成
- **维护状态**：**维护中但不活跃**——代码偶尔收到编译修复，但无新功能开发
- **已知限制**：
  - `EnabledByDefault: false`，需手动在项目设置中启用
  - 实际的 ARKit 调用仅在 iOS 平台编译（`#if SUPPORTS_ARKIT_1_0`），桌面端仅作为数据接收方
  - `SupportedPrograms` 限制为 `LiveLinkHub`
  - 远程 UDP 传输使用自定义二进制协议（版本 6），非标准 LiveLink 网络协议
- **推荐**：如果你需要在 UE5 中使用 Apple ARKit 面部追踪，这是官方唯一选择，功能完整且稳定，推荐使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport)
- [AppleARKit 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)（底层 ARKit 集成）
- [Apple ARKit 面部追踪文档](https://developer.apple.com/documentation/arkit/tracking_and_visualizing_faces)
- [UE5 LiveLink 文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)
