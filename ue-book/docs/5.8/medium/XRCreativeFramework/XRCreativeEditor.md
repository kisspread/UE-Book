# XR Creative Framework

> 

| 属性 | 值 |
|---|---|
| 中文名 | XR 创意框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRCreative` (Runtime), `XRCreativeEditor` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2023-02-14 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework) | |

## 用途

XR Creative Framework 为虚拟制作（Virtual Production）工作流提供了一个基于 XR（扩展现实）的编辑器模式和工具框架。它通过继承 `UVREditorModeBase`，在虚幻编辑器中集成一个完整的 VR 编辑环境。该插件的核心价值在于它定义了 VR 编辑模式的状态管理（进入/退出/切换）、头部和房间变换跟踪、手柄激光交互等基础接口，并提供了 `XRCreativeEditorUtilityToolActor` 作为在编辑器内（包括 VR 模式下）接收输入和运行逻辑的工具 Actor 基类。它旨在为虚拟制作的 XR 创意环节（如 VR 场景预览、空间布局、工具开发）提供一个标准化的、可扩展的底层框架。

## 使用场景

- **XR 导演/美术**：需要在 VR 中预览和编辑虚拟场景，进行空间布局和构图。
- **虚拟制作工具开发者**：需要为虚拟制作流程开发自定义的 XR 工具（例如，一个在 VR 中绘制标记的工具），需要处理 VR 输入、变换同步和编辑器事件。
- **技术美术/开发者**：希望为自定义的 VR 编辑模式或工具集提供一个稳定的起点和基础功能。

## 蓝图用法

该插件的蓝图 API 主要围绕 VR 编辑模式的状态控制和变换获取/设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRoomTransform` | 获取当前 VR 编辑模式中“房间”坐标系相对于世界坐标系的变换。 | `UXRCreativeVREditorMode` |
| `SetRoomTransform` | 设置当前 VR 编辑模式中“房间”坐标系相对于世界坐标系的变换。 | `UXRCreativeVREditorMode` |
| `GetHeadTransform` | 获取当前 VR 头显相对于世界坐标系的变换。 | `UXRCreativeVREditorMode` |
| `SetHeadTransform` | 设置当前 VR 头显相对于世界坐标系的变换。 | `UXRCreativeVREditorMode` |
| `Run` | 执行此工具 Actor 的标准功能。 | `AXRCreativeEditorUtilityToolActor` |
| `GetReceivesEditorInput` | 获取该工具 Actor 是否接收编辑器输入。 | `AXRCreativeEditorUtilityToolActor` |
| `SetReceivesEditorInput` | 设置该工具 Actor 是否接收编辑器输入。 | `AXRCreativeEditorUtilityToolActor` |
| `GetInputComponent` | 获取此工具 Actor 当前的编辑器输入组件。 | `AXRCreativeEditorUtilityToolActor` |

**蓝图可实现事件（在 `UXRCreativeVREditorMode` 子类中覆盖）：**
- `On Enter`：进入 VR 编辑模式时调用。
- `On Exit`：退出 VR 编辑模式时调用。
- `Tick`：VR 编辑模式每帧调用。

### 使用示例（蓝图描述）

1.  **创建自定义 VR 编辑模式**：创建一个继承自 `UXRCreativeVREditorMode` 的蓝图类（例如 `BP_MyVREditorMode`）。
2.  **实现进入/退出逻辑**：在 `BP_MyVREditorMode` 中，覆盖 `On Enter` 和 `On Exit` 事件，用于初始化和清理 VR 环境下的自定义逻辑（如显示 UI、加载特定资产）。
3.  **处理每帧逻辑**：覆盖 `Tick` 事件，可以获取 `GetRoomTransform` 或 `GetHeadTransform`，并基于此更新场景中的物体位置。
4.  **创建并使用工具 Actor**：在场景中放置一个继承自 `AXRCreativeEditorUtilityToolActor` 的蓝图 Actor（例如 `BP_MyVRSketchTool`）。
5.  **配置输入**：在 `BP_MyVRSketchTool` 的细节面板中，勾选 `Receives Editor Input`。然后，在事件图表中，可以绑定到标准的 `Enhanced Input` 事件（如 `IA_Trigger`），这些事件会在 VR 模式下通过手柄触发时调用。
6.  **关联模式与工具**：在 `BP_MyVREditorMode` 中，通过 `ToolsetClass` 属性指定一个包含 `BP_MyVRSketchTool` 等工具的 `XRCreativeToolset` 资产，以便在进入该模式时自动激活相关工具。

## C++ 用法

### 头文件引入

```cpp
// 使用 XR Creative 核心功能
#include "XRCreativeModule.h" // 如果存在，通常对应 XRCreative 模块

// 使用编辑器模式和工具 Actor
#include "XRCreativeVREditorMode.h"
#include "XRCreativeEditorUtilityToolActor.h"
```

### 基本用法

创建一个自定义的 VR 编辑模式类。
（基于 `XRCreativeVREditorMode.h` 头文件分析）

```cpp
// MyCustomVREditorMode.h
#pragma once
#include "XRCreativeVREditorMode.h"
#include "MyCustomVREditorMode.generated.h"

UCLASS()
class UMyCustomVREditorMode : public UXRCreativeVREditorMode
{
    GENERATED_BODY()

public:
    // 覆盖进入模式，添加自定义逻辑
    virtual void Enter() override
    {
        Super::Enter();
        // 在此处初始化你的自定义 VR 编辑环境
        UE_LOG(LogXRCreativeEditor, Log, TEXT("Entering My Custom VR Editor Mode."));
    }

    // 覆盖蓝图可实现的进入事件（如果需要进行蓝图扩展）
    UFUNCTION(BlueprintImplementableEvent, meta=(DisplayName="On My Custom Enter"))
    void BP_OnMyCustomEnter();

    // 覆盖 Tick 以进行自定义每帧更新
    virtual void Tick(float InDeltaSeconds) override
    {
        Super::Tick(InDeltaSeconds);
        // 在此处添加每帧逻辑，例如：
        FTransform HeadPose = GetHeadTransform();
        // ... 对 HeadPose 进行处理
    }
};
```

### 进阶用法

创建一个在 VR 模式下接收输入并执行动作的编辑器工具。
（基于 `XRCreativeEditorUtilityToolActor.h` 头文件分析）

```cpp
// VRSketchTool.h
#pragma once
#include "XRCreativeEditorUtilityToolActor.h"
#include "VRSketchTool.generated.h"

UCLASS()
class AVRSketchTool : public AXRCreativeEditorUtilityToolActor
{
    GENERATED_BODY()

public:
    AVRSketchTool();

    // 实现标准的“运行”功能
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "VR Tools")
    void Run();
    virtual void Run_Implementation() override;

    // 可以重写构造函数来设置默认属性
    virtual void OnConstruction(const FTransform& Transform) override;
};
```

## Demo 示例

一个最小的自定义 VR 编辑模式 C++ 类头文件和实现。

```cpp
// MyMinimalVREditorMode.h
#pragma once
#include "XRCreativeVREditorMode.h"
#include "MyMinimalVREditorMode.generated.h"

UCLASS()
class UMyMinimalVREditorMode : public UXRCreativeVREditorMode
{
    GENERATED_BODY()

protected:
    virtual void Enter() override;
    virtual void Exit(bool bInShouldDisableStereo) override;
    virtual void Tick(float InDeltaSeconds) override;
};
```

```cpp
// MyMinimalVREditorMode.cpp
#include "MyMinimalVREditorMode.h"

void UMyMinimalVREditorMode::Enter()
{
    Super::Enter();
    // 初始化逻辑
}

void UMyMinimalVREditorMode::Exit(bool bInShouldDisableStereo)
{
    // 清理逻辑
    Super::Exit(bInShouldDisableStereo);
}

void UMyMinimalVREditorMode::Tick(float InDeltaSeconds)
{
    Super::Tick(InDeltaSeconds);
    FTransform Head = GetHeadTransform();
    // 在 VR 中跟踪头部位置的示例逻辑
}
```

## 模块依赖

基于 `XRCreativeEditor` 作为 Runtime 模块的属性，以及其功能（VR 编辑模式、编辑器工具）推断，其依赖应主要包括：

| 模块 | 用途 |
|---|---|
| `XRCreative` | 提供该框架的核心运行时类型和功能。 |
| `VREditor` | 提供 `UVREditorModeBase` 基类和 VR 编辑器交互的基础。 |
| `EnhancedInput` | （可能）用于处理来自 VR 控制器的编辑器内输入。 |

*注：此列表基于功能推断，完整准确的依赖需查看 `XRCreativeEditor.Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `998bea39` | [XR Creative] - Fix regression where actors moved with the VR Gizmo then can't be selected because t | 修复使用 VR Gizmo 移动 Actor 后无法选中的回归性问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举使用导致输出乱码的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

该插件创建于 2023 年 2 月，目前处于**实验性**（Beta）状态，且未默认启用。从近期（2026 年 5 月）的提交记录来看，插件仍在**活跃维护**中，主要进行 Bug 修复（如 VR Gizmo 选择问题、日志输出问题）和代码现代化更新（迁移日志宏、清理废弃代码）。作为 Epic Games 官方维护的虚拟制作基础框架，其稳定性与未来版本的兼容性预计会得到持续保障。鉴于其“实验性”标签，建议在生产环境中谨慎评估，但非常适合用于工具原型开发和对 XR 编辑工作流的研究。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/XRCreativeFramework)
- 官方文档（暂无）
- 测试用例（插件目录内未发现公开测试用例）