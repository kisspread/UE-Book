# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器设置） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 用途

此插件是一套用于虚拟制作（Virtual Production）工作流的编辑器与运行时工具集。它旨在解决虚拟拍摄中场景管理、设备同步和编辑器扩展的常见需求。具体包括：
- **VR场景审查与交互**：提供VR编辑模式下的子系统，用于管理UI面板、手势、移动速度等（注：此部分功能在5.5版本后已标记为废弃，计划移除）。
- **编辑器内可Tick的Actor**：提供能够在编辑器视口内持续更新的Actor基类，用于实现自定义的编辑器交互逻辑，例如实时预览或设备控制。
- **时间码与Genlock集成**：包含用于显示和管理时间码提供者（TimecodeProvider）和Genlock同步状态的Slate UI组件。
- **OSC（开放式声音控制）支持**：内置OSC服务器管理，便于与外部设备进行通信。
- **蓝图函数库**：提供一系列便捷的蓝图函数，用于导入快照、生成编辑器Actor等。

## 使用场景

- 你需要在UE编辑器内为虚拟拍摄现场的LED墙或监视器生成实时预览或控制界面时。
- 你的工作流依赖于OSC协议与灯光控制台、运动控制设备或其他外部硬件进行通信时。
- 你需要在编辑器中创建一个持续运行的逻辑组件（例如读取传感器数据或控制设备），而不希望它被保存到关卡中时。
- 你需要为编辑器界面添加自定义的时间码显示或Genlock状态监控面板时。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnVPEditorTickableActor` | 生成一个可保存、支持多用户同步的编辑器Tick Actor | `UVPUtilitiesEditorBlueprintLibrary` |
| `SpawnVPTransientEditorTickableActor` | 生成一个不保存、不同步的瞬态编辑器Tick Actor | `UVPUtilitiesEditorBlueprintLibrary` |
| `ImportSnapshotTexture` | 将图像文件导入到项目的虚拟制作快照文件夹中 | `UVPUtilitiesEditorBlueprintLibrary` |
| `GetDefaultOSCServer` | 获取模块启动时自动创建的默认OSC服务器实例 | `UVPUtilitiesEditorBlueprintLibrary` |
| `ToggleVRScoutingUI` | (已废弃) 打开/关闭VR侦察模式的浮动UI面板 | `UVPScoutingSubsystem` |
| `EnterVRMode` | (已废弃) 进入VR编辑模式 | `UVPScoutingSubsystem` |
| `ExitVRMode` | (已废弃) 退出VR编辑模式 | `UVPScoutingSubsystem` |

### 使用示例（蓝图描述）

1.  **创建一个编辑器内持续运行的逻辑Actor**：
    *   使用 `SpawnVPEditorTickableActor` 节点，指定一个从 `AVPEditorTickableActorBase` 派生的类。
    *   该Actor的 `Receive Editor Tick` 事件将在编辑器运行时每帧被调用，你可以在其中放置读取设备数据或更新预览的逻辑。
    *   **注意**：此类Actor会被保存到关卡，并在多用户编辑时同步操作。

2.  **在蓝图中使用OSC服务器**：
    *   调用 `GetDefaultOSCServer` 节点获取全局的 `UOSCServer` 对象引用。
    *   通过此引用，可以绑定OSC地址监听器（使用 `BindEvent`），在接收到外部设备消息时执行蓝图逻辑。
    *   需在项目设置（Virtual Production Utilities）中配置OSC服务器地址和端口。

## C++ 用法

### 头文件引入

```cpp
#include "IVPUtilitiesEditorModule.h"
#include "VPUtilitiesEditorBlueprintLibrary.h"
#include "VPEditorTickableActorBase.h"
```

### 基本用法

**获取模块接口与访问蓝图库函数**
```cpp
// 获取编辑器模块单例
IVPUtilitiesEditorModule& EditorModule = IVPUtilitiesEditorModule::Get();

// 获取默认的OSC服务器
UOSCServer* OSCServer = EditorModule.GetOSCServer();

// 或通过蓝图库函数获取
UOSCServer* OSCServer2 = UVPUtilitiesEditorBlueprintLibrary::GetDefaultOSCServer();

// 生成一个瞬态编辑器Actor
FVector Location(0.f);
FRotator Rotation(0.f);
UWorld* World = GEditor->GetEditorWorldContext().World();
AVPTransientEditorTickableActorBase* TransientActor = UVPUtilitiesEditorBlueprintLibrary::SpawnVPTransientEditorTickableActor(World, MyTransientActorClass, Location, Rotation);
```

### 进阶用法

**创建自定义的编辑器Tick Actor**
```cpp
// MyCustomEditorActor.h
#pragma once
#include "VPEditorTickableActorBase.h"
#include "MyCustomEditorActor.generated.h"

UCLASS()
class AMyCustomEditorActor : public AVPEditorTickableActorBase
{
    GENERATED_BODY()

public:
    // 在编辑器视口中每帧调用
    virtual void EditorTick(float DeltaTime) override
    {
        // 在此处添加自定义逻辑，例如读取串口数据、更新预览等
    }
};
```

**使用时间码显示控件**
```cpp
// 在自定义的Slate Widget中添加时间码显示
#include "STimecodeProvider.h"

// 在Construct函数中
ChildSlot
[
    SNew(STimecodeProvider)
    .DisplayFrameRate(true)
    .DisplaySynchronizationState(true)
];
```

## Demo 示例

**一个使用OSC服务器并每帧打印信息的编辑器Actor**

```cpp
// OSCMonitoringActor.h
#pragma once
#include "VPEditorTickableActorBase.h"
#include "OSCMonitoringActor.generated.h"

class UOSCServer;

UCLASS()
class AOSCMonitoringActor : public AVPEditorTickableActorBase
{
    GENERATED_BODY()

public:
    AOSCMonitoringActor();

    virtual void EditorTick(float DeltaTime) override;

private:
    UPROPERTY(Transient)
    TObjectPtr<UOSCServer> BoundOSCServer;
};
```

```cpp
// OSCMonitoringActor.cpp
#include "OSCMonitoringActor.h"
#include "VPUtilitiesEditorBlueprintLibrary.h"
#include "OSCServer.h"

AOSCMonitoringActor::AOSCMonitoringActor()
{
    // 获取并绑定默认的OSC服务器
    BoundOSCServer = UVPUtilitiesEditorBlueprintLibrary::GetDefaultOSCServer();
    if (BoundOSCServer)
    {
        // 例如，监听来自控制器的消息
        BoundOSCServer->BindEvent(TEXT("/controller/trigger"), [this](const FOSCMessage& Message)
        {
            UE_LOG(LogTemp, Log, TEXT("OSC Trigger Received!"));
        });
    }
}

void AOSCMonitoringActor::EditorTick(float DeltaTime)
{
    // 每帧打印一个简单的状态信息，证明Actor在编辑器中运行
    UE_LOG(LogTemp, Verbose, TEXT("OSCMonitoringActor Ticking. DeltaTime: %f"), DeltaTime);
}
```

**使用方式**：在蓝图中，使用 `SpawnVPEditorTickableActor` 节点并选择 `AOSCMonitoringActor` 类生成该Actor。

## 模块依赖

从插件源码结构推断，使用本插件功能通常无需特殊模块依赖，主要通过插件自身提供的接口和蓝图库访问。但若在项目中实现依赖此插件的自定义模块，可能需要：

| 模块 | 用途 |
|---|---|
| `VREditor` | 用于访问VR编辑器模式相关功能（废弃部分可能依赖） |
| `OSC` | 用于访问OSC服务器和消息类 |
| `TimeManagement` | 用于时间码和Genlock相关的底层支持 |
| `Slate`, `SlateCore`, `UMG` | 用于编辑器UI扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `02b15f1b` | Remove redundant texture update call so that snapshot texture is always updated properly | 修复快照纹理更新问题 |
| 2026-04-20 | `766d0ed3` | [VPUtilities & TimeManagement] Moved Timecode custom timestep to the TimeManagement engine module so | 将时间码自定义时间步长功能迁移至TimeManagement模块 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移为UE_LOGF格式 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏控件功能移至新的非实验性插件中 |
| 2026-02-05 | `25fe0362` | Deprecate FViewportFrame | 废弃FViewportFrame类 |

### 维护评价

**状态：活跃重构与迁移中**

-   **年龄**：该插件创建于2019年，已有约7年历史，属于老古董级别。
-   **近期活动**：最近（2026年）仍有密集的更新，但主要工作集中在**清理废弃代码、迁移功能到更稳定的模块**（如TimeManagement、ViewportWidgetOverlay插件）。核心的VR侦察（Scouting）子系统已标记为废弃，并计划在UE5.7移除。
-   **已知限制与风险**：
    1.  **实验性与废弃**：插件本身为实验性（IsBetaVersion=true），且包含大量`UE_DEPRECATED`标记的代码。新项目应避免使用已废弃的功能。
    2.  **功能迁移**：部分核心功能（如自定义时间步长、全屏控件）正在被移出此插件，使用者需要关注后续版本的迁移指南。
    3.  **默认禁用**：插件默认未启用，需要手动在插件列表中开启。
-   **推荐使用建议**：
    -   **对于新项目**：可以评估其提供的**编辑器Tick Actor基类**和**OSC集成**功能是否仍符合需求，但对任何标记为“已废弃”的API应保持警惕，并做好未来迁移的准备。
    -   **对于维护旧项目**：如果项目已依赖此插件且功能稳定，可继续使用，但应密切注意引擎升级时的兼容性问题，并逐步替换掉已废弃的API。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities)
-   [官方文档]() （无）
-   [测试用例]() （未在插件目录内发现标准测试文件）