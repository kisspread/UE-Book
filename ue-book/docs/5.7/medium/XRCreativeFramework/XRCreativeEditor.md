# XR Creative Framework

> （Description 为空）

| 属性 | 值 |
|---|---|
| 中文名 | XR 创作框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-10-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/XRCreativeFramework) | |

## 用途

XR Creative Framework 是 Epic Games 提供的实验性 VR 编辑器扩展框架。它基于现有的 `VREditorModeBase` 构建了一套可扩展的 VR 编辑模式，允许开发者在 VR 环境中创建自定义的创作工具集。核心组件包括：

- **VR 编辑器模式** (`UXRCreativeVREditorMode`)：封装了 VR 模式的生命周期（进入/退出、立体渲染、房间变换、手柄激光等），并暴露蓝图事件（OnEnter/OnExit/Tick）方便自定义行为。
- **编辑器工具 Actor** (`AXRCreativeEditorUtilityToolActor`)：一个可放置在世界中的蓝图基类，自带编辑器输入组件，可在 VR 编辑器中响应输入事件，执行自定义工具逻辑（`Run` 事件）。

该框架解决了在 VR 中快速搭建交互式创作工具的重复性问题，为虚拟制作、VR 场景布局等场景提供了标准化入口。

## 使用场景

- **虚拟制作**：导演或美术人员在 VR 中查看场景，并使用手持工具调整灯光、摄像机、道具位置。
- **VR 场景编辑工具**：开发专用于 VR 的拖放工具、测量工具、标记工具等，无需为每个工具重新实现 VR 模式逻辑。
- **教育与演示**：构建沉浸式编辑器演示，允许用户通过 VR 控制器直接与环境交互。

## 蓝图用法

以下节点均可在蓝图图表中使用，前提是项目已启用该插件并正确配置。

### 核心节点（VREditorMode 基类）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enter` | 进入 VR 模式（自动调用 `BP_OnEnter` 事件） | `UXRCreativeVREditorMode` |
| `Exit` | 退出 VR 模式（自动调用 `BP_OnExit` 事件） | `UXRCreativeVREditorMode` |
| `Tick` (蓝图实现事件) | 每帧触发，DeltaSeconds 为参数 | `UXRCreativeVREditorMode` |
| `Get Room Transform` | 获取房间（摄像机追踪原点）的全局变换 | `UXRCreativeVREditorMode` |
| `Set Room Transform` | 设置房间变换，用于重新定位 VR 原点 | `UXRCreativeVREditorMode` |
| `Get Head Transform` | 获取头戴设备的全局变换 | `UXRCreativeVREditorMode` |
| `Set Head Transform` | 设置头戴设备变换（通常用于测试或重定位） | `UXRCreativeVREditorMode` |
| `Get Laser For Hand` | 获取指定手柄（左手/右手）的激光起点和终点 | `UXRCreativeVREditorMode` |
| `Wants To Exit Mode` | 返回是否请求退出 VR 模式（布尔值） | `UXRCreativeVREditorMode` |

### 核心节点（EditorUtilityToolActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Run` (蓝图可重写事件) | 执行工具逻辑，由外部调用触发 | `AXRCreativeEditorUtilityToolActor` |
| `Get Input Component` | 获取编辑器输入组件（纯函数） | `AXRCreativeEditorUtilityToolActor` |
| `Get Receives Editor Input` | 获取是否接收编辑器输入（纯函数） | `AXRCreativeEditorUtilityToolActor` |
| `Set Receives Editor Input` | 启用/禁用编辑器输入（Setter） | `AXRCreativeEditorUtilityToolActor` |

### 蓝图使用示例

1. **创建一个自定义 VR 编辑模式**：  
   - 创建一个继承自 `UXRCreativeVREditorMode` 的蓝图类。
   - 在事件图表中实现 `On Enter`（自动调用 `BP_OnEnter`）时显示自定义 UI 或激活工具 Actor。
   - 在 `Tick` 事件中更新工具状态或检测手势。

2. **创建一个 VR 工具 Actor**：  
   - 创建一个继承自 `AXRCreativeEditorUtilityToolActor` 的蓝图类。
   - 将 `bReceivesEditorInput` 设为 `true`。
   - 在 `Run` 事件中编写工具逻辑，例如在 VR 中生成一个 Actor 并附着在控制器上。
   - 使用 `GetInputComponent` 绑定按键或执行自定义输入处理。

## C++ 用法

### 头文件引入

```cpp
#include "XRCreativeVREditorMode.h"
#include "XRCreativeEditorUtilityToolActor.h"
```

### 基本用法：自定义 VR 编辑模式

继承 `UXRCreativeVREditorMode` 并重写必要虚函数。以下示例展示了如何在 C++ 中创建自定义 VR 模式（来源：根据类声明推断，实际使用时需配合模块注册）。

```cpp
// MyVREditorMode.h
#pragma once

#include "XRCreativeVREditorMode.h"
#include "MyVREditorMode.generated.h"

UCLASS()
class MYPROJECT_API UMyVREditorMode : public UXRCreativeVREditorMode
{
    GENERATED_BODY()

public:
    virtual void Enter() override;
    virtual void Exit(bool bInShouldDisableStereo) override;
    virtual void Tick(float InDeltaSeconds) override;

    // 重写激光获取，自定义逻辑
    virtual bool GetLaserForHand(EControllerHand InHand, FVector& OutLaserStart, FVector& OutLaserEnd) const override;
};
```

```cpp
// MyVREditorMode.cpp
#include "MyVREditorMode.h"

void UMyVREditorMode::Enter()
{
    Super::Enter();
    // 自定义初始化逻辑，例如生成 Avatar
}

void UMyVREditorMode::Exit(bool bInShouldDisableStereo)
{
    // 清理逻辑
    Super::Exit(bInShouldDisableStereo);
}

void UMyVREditorMode::Tick(float InDeltaSeconds)
{
    Super::Tick(InDeltaSeconds);
    // 每帧更新
}

bool UMyVREditorMode::GetLaserForHand(EControllerHand InHand, FVector& OutLaserStart, FVector& OutLaserEnd) const
{
    // 自定义激光起点和终点
    return Super::GetLaserForHand(InHand, OutLaserStart, OutLaserEnd);
}
```

### 进阶用法：编辑器工具 Actor 与输入

通过 `AXRCreativeEditorUtilityToolActor` 子类，可以在 VR 编辑模式下响应输入并执行工具逻辑。

```cpp
// MyVRTool.h
#pragma once

#include "XRCreativeEditorUtilityToolActor.h"
#include "MyVRTool.generated.h"

UCLASS()
class MYPROJECT_API AMyVRTool : public AXRCreativeEditorUtilityToolActor
{
    GENERATED_BODY()

public:
    virtual void Run() override;
    virtual void Tick(float DeltaSeconds) override;
};
```

```cpp
// MyVRTool.cpp
#include "MyVRTool.h"
#include "Kismet/GameplayStatics.h"

void AMyVRTool::Run()
{
    // 工具激活时的逻辑，例如在控制器位置生成一个球体
    if (UInputComponent* Input = GetInputComponent())
    {
        // 绑定按键：例如按 'Action' 键执行操作
        Input->BindAction("VRTool_Action", IE_Pressed, this, &AMyVRTool::OnActionPressed);
    }
}

void AMyVRTool::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    // 每帧更新工具状态
}

void AMyVRTool::OnActionPressed()
{
    // 在 VR 中执行操作，例如生成 Actor
    FVector Location = GetActorLocation();
    FRotator Rotation = GetActorRotation();
    GetWorld()->SpawnActor<AActor>(SomeBlueprintClass, Location, Rotation);
}
```

## Demo 示例

以下是一个最小 C++ 模块示例，展示如何创建自定义 VR 编辑模式并注册到编辑器。假设你的模块名称为 `MyXRCreativeDemo`，且已添加对 `XRCreativeEditor` 的依赖。

### MyXRCreativeDemoModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyXRCreativeDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyXRCreativeDemoModule.cpp

```cpp
#include "MyXRCreativeDemoModule.h"
#include "MyCustomVREditorMode.h"  // 你自定义的 VR 模式类
#include "Editor/VREditorMode.h"
#include "Editor/UnrealEdEngine.h"
#include "UnrealEdGlobals.h"

#define LOCTEXT_NAMESPACE "FMyXRCreativeDemoModule"

void FMyXRCreativeDemoModule::StartupModule()
{
    // 注册自定义 VR 模式到编辑器
    if (UUnrealEdEngine* EdEngine = Cast<UUnrealEdEngine>(GEngine))
    {
        // 注意：VREditorModeBase 需要通过编辑器扩展系统注册
        // 此处仅展示概念，实际注册方式因版本而异
    }
}

void FMyXRCreativeDemoModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyXRCreativeDemoModule, MyXRCreativeDemo);
```

## 模块依赖

从 `XRCreativeEditor.Build.cs` 推断（由于未提供完整源码，以下为基于编辑器模块通用依赖的合理列表）：

| 模块 | 用途 |
|---|---|
| `VREditor` | 提供 `UVREditorModeBase` 基础类 |
| `UMG` | 用户界面组件（WidgetComponent 等） |
| `EnhancedInput` | 处理 VR 控制器输入（头文件中有引用 `IEnhancedInputSubsystemInterface`） |
| `HeadMountedDisplay` | 头戴显示设备接口（可能依赖） |
| `XRCreative` | 运行时模块，提供共享数据或工具集（如 `UXRCreativeToolset`） |

如果你的模块需要引用 `XRCreativeEditor`，在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "XRCreativeEditor",
    "VREditor",
    "EnhancedInput",
});
```

## 维护状态

### 近期更新

- 2025-09-23 `9feb681f` — VR Editor: Fix for failed check in UWidgetComponent unregister during engine pre-exit.
- 2024-11-28 `eca86263` — Remove the check for r.PostProcess.PropagateAlpha in the XR Creative ::ValidateSettings(). This is ...
- 2024-11-28 `be437642` — Created missing Get/Set functions for the following member variables: ...
- 2024-10-30 `d4d88219` — Removed more includes of SceneManagement.h in favor of the needed includes
- 2024-10-15 `08bf24fa` — VR Editor: Fixes a regression from CL 36864748 that led to FSlateRHIRenderer not correctly interoper

### 维护评价

| 维度 | 评价 |
|---|---|
| 创建时间 | 2024-10-15（约 1 年前） |
| 最近更新 | 2025-09-23（约 1 周前）有功能性修复 |
| 活跃度 | 较低：仅 5 次 commit，且多数为修复或重构 |
| 实验性标志 | ⚠️ 是（`IsBetaVersion=true`） |
| 推荐使用 | ⚠️ 谨慎：插件仍处于 Beta 阶段，API 可能不稳定；但基本框架可用，适合探索性项目 |

总体而言，该插件自创建以来更新频率较低，但仍在维护（最近有修复提交）。作为实验性插件，适合用于虚拟制作的原型开发，不建议直接用于发布版本，除非充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/XRCreativeFramework)
- [头文件目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/XRCreativeFramework/Source/XRCreativeEditor/Public)