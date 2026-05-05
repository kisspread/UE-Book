# Motion Design Scene State

> （.uplugin Description 为空，基于源码分析）为 Motion Design 虚拟制片场景提供可视化状态机系统，支持状态定义、事件驱动转换、属性绑定和任务执行。

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、图表模板） |
| 模块 | `SceneState` (Runtime), `SceneStateBinding` (Runtime), `SceneStateEvent` (Runtime), `SceneStateTasks` (Runtime), `SceneStateGameplay` (Runtime), `SceneStateBlueprint` (Runtime), `SceneStateBlueprintEditor` (Runtime), `SceneStateMachineGraph` (Runtime), `SceneStateEventGraph` (Runtime), `SceneStateTransitionGraph` (Runtime), `SceneStateEditor` (Runtime), `SceneStateEventEditor` (Runtime), `SceneStateGameplayEditor` (Runtime), `SceneStateMachineEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState) | |

---

## 用途

Scene State 是一个面向 **Motion Design（动态图形设计）** 和 **虚拟制片** 场景的状态机管理系统。它解决的核心问题是：**在广播、电视、虚拟制片等场景中，需要对场景中的元素进行状态化管理**——例如一个演播室画面需要在"开场"、"主画面"、"嘉宾特写"、"结尾"等状态之间切换，每个状态对应不同的属性配置和自动化任务。

该插件提供了一套完整的可视化状态机编辑器（类似动画蓝图的状态机，但面向场景状态），核心能力包括：

- **可视化状态机图**：通过节点图定义状态（State）和转换（Transition），支持嵌套状态机
- **属性绑定系统**（Property Binding）：将状态机内部数据绑定到外部 Actor/Component 的属性上，实现状态变化自动驱动场景属性更新
- **任务系统**（Tasks）：在状态进入/退出时执行自定义任务逻辑，任务本身也可以用蓝图定义
- **事件系统**（Events）：基于事件驱动的状态转换，支持自定义事件图
- **蓝图集成**：状态机本身以蓝图资产形式存在（`USceneStateBlueprint`），支持蓝图编译、调试和热重载

与 UE 内置的 Animation Blueprint 状态机类似，但目标对象不是骨骼动画而是场景状态，专为 Motion Design 工作流设计。

## 使用场景

- 你在做虚拟制片的演播室图形系统 → 用 Scene State 管理画面状态切换（如 Lower Third、Full Screen、Logo Bug 等）
- 你需要在 Motion Design 场景中定义复杂的状态转换逻辑 → 用状态机图可视化编辑
- 你需要状态变化时自动更新场景中多个对象的属性 → 用属性绑定系统
- 你需要在进入某个状态时触发自动化操作（播放动画、切换材质等）→ 用任务系统
- 你需要基于外部事件（用户输入、网络消息等）驱动状态转换 → 用事件系统

## 蓝图用法

该插件的核心交互以 **专用蓝图资产** 和 **可视化图表编辑器** 为主，而非传统的 BlueprintCallable 节点。主要工作流如下：

### 资产类型

| 资产类型 | 说明 | 对应类 |
|---|---|---|
| Scene State Blueprint | 主状态机蓝图，包含状态机图、属性绑定和任务定义 | `USceneStateBlueprint` |
| Scene State Task Blueprint | 任务蓝图，定义可在状态中执行的自定义任务逻辑 | `USceneStateTaskBlueprint` |

### 核心工作流

1. **创建 Scene State Blueprint 资产**：在内容浏览器右键 → Animation → Motion Design Scene State Blueprint
2. **编辑状态机图**：双击打开蓝图，在状态机图中添加状态节点、定义转换条件
3. **配置属性绑定**：在蓝图的绑定面板中，将状态机内部属性绑定到外部对象
4. **定义任务**：为每个状态配置进入/退出时执行的任务
5. **调试**：运行时选择调试对象，观察状态机执行流程

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRootId` | 获取状态机根节点的唯一标识 | `USceneStateBlueprint` |
| `GetBindingCollection` | 获取属性绑定集合（编辑器用） | `USceneStateBlueprint` |
| `GetBindingStructs` | 获取指定结构体 ID 的可绑定描述符列表 | `USceneStateBlueprint` |
| `FindExtension` | 查找指定类型的蓝图扩展 | `USceneStateBlueprint` |
| `CreateRootBinding` | 创建根绑定描述符 | `USceneStateBlueprint` |

### 使用示例（蓝图描述）

1. 在内容浏览器创建 **Motion Design Scene State Blueprint** 资产
2. 打开蓝图编辑器，会看到状态机图编辑区域
3. 右键添加 **State** 节点，命名为 "Intro"、"Main"、"Outro"
4. 从一个 State 拖拽到另一个 State 创建 **Transition**
5. 在 Transition 上设置转换条件（事件触发、时间延迟等）
6. 选中某个 State，在细节面板中配置 **Tasks**（进入时执行的任务）
7. 在蓝图的 **Binding** 面板中，将状态数据绑定到场景中 Actor 的属性
8. 运行时，状态机会根据事件和条件自动切换状态，绑定的属性随之更新

## C++ 用法

### 头文件引入

```cpp
#include "SceneStateBlueprint.h"
#include "SceneStateBindingCollection.h"
#include "SceneStateBindingDesc.h"
```

### 基本用法

获取 Scene State Blueprint 的绑定信息：

```cpp
// 获取一个已加载的 Scene State Blueprint
USceneStateBlueprint* SceneStateBlueprint = LoadObject<USceneStateBlueprint>(nullptr, TEXT("/Game/MySceneStateBP"));

if (SceneStateBlueprint)
{
    // 获取根状态 ID
    const FGuid& RootId = SceneStateBlueprint->GetRootId();
    
    // 获取绑定集合
    FSceneStateBindingCollection& BindingCollection = SceneStateBlueprint->GetBindingCollection();
    
    // 获取根绑定描述
    FSceneStateBindingDesc RootBinding = SceneStateBlueprint->CreateRootBinding();
}
```

### 进阶用法

查询可绑定结构体和函数：

```cpp
// 查询某个结构体 ID 的所有可绑定属性
USceneStateBlueprint::FGetBindableStructsParams Params;
Params.TargetStructId = SomeStructId;
Params.bIncludeGlobalDescs = true;   // 包含全局绑定
Params.bIncludeFunctions = true;     // 包含绑定函数

TArray<TInstancedStruct<FSceneStateBindingDesc>> BindingDescs;
SceneStateBlueprint->GetBindingStructs(Params, BindingDescs);

// 遍历所有绑定函数
SceneStateBlueprint->ForEachBindingFunction(
    [](const FSceneStateBindingFunction& InFunction, const FPropertyBindingBinding& InBinding) -> bool
    {
        // 处理每个绑定函数
        // 返回 true 继续遍历，返回 false 停止
        return true;
    }
);

// 通过 ID 查找可绑定结构体
TInstancedStruct<FPropertyBindingBindableStructDescriptor> OutDesc;
bool bFound = SceneStateBlueprint->GetBindableStructByID(SomeStructId, OutDesc);

// 获取绑定数据视图（运行时数据访问）
FPropertyBindingDataView DataView;
bool bHasData = SceneStateBlueprint->GetBindingDataViewByID(SomeStructId, DataView);
```

监听调试对象变化（来自 `SceneStateBlueprintDelegates.h`）：

```cpp
#include "SceneStateBlueprintDelegates.h"

// 监听蓝图调试对象变化
UE::SceneState::Graph::OnBlueprintDebugObjectChanged.AddLambda(
    [](const UE::SceneState::Graph::FBlueprintDebugObjectChange& Change)
    {
        USceneStateBlueprint* Blueprint = Change.Blueprint;
        UObject* NewDebugObject = Change.DebugObject;
        // 处理调试对象变化
    }
);
```

## Demo 示例

### 场景状态蓝图的程序化访问

```cpp
// MySceneStateManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySceneStateManager.generated.h"

class USceneStateBlueprint;

UCLASS()
class AMySceneStateManager : public AActor
{
    GENERATED_BODY()

public:
    AMySceneStateManager();

    /** 要驱动的 Scene State Blueprint 资产 */
    UPROPERTY(EditAnywhere, Category = "Scene State")
    TSoftObjectPtr<USceneStateBlueprint> SceneStateAsset;

    /** 初始化状态机 */
    UFUNCTION(BlueprintCallable, Category = "Scene State")
    void InitializeStateMachine();

    /** 获取当前绑定集合中的所有可绑定结构体 */
    void QueryBindableStructs();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<USceneStateBlueprint> LoadedBlueprint;
};
```

```cpp
// MySceneStateManager.cpp
#include "MySceneStateManager.h"
#include "SceneStateBlueprint.h"
#include "SceneStateBindingCollection.h"
#include "SceneStateBindingDesc.h"

AMySceneStateManager::AMySceneStateManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMySceneStateManager::BeginPlay()
{
    Super::BeginPlay();
    InitializeStateMachine();
}

void AMySceneStateManager::InitializeStateMachine()
{
    LoadedBlueprint = SceneStateAsset.LoadSynchronous();
    if (!LoadedBlueprint)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load Scene State Blueprint"));
        return;
    }

    // 获取根状态 ID
    const FGuid& RootId = LoadedBlueprint->GetRootId();
    UE_LOG(LogTemp, Log, TEXT("Scene State Root ID: %s"), *RootId.ToString());

    // 获取绑定集合
    const FSceneStateBindingCollection& Bindings = LoadedBlueprint->GetBindingCollection();
    UE_LOG(LogTemp, Log, TEXT("Binding collection loaded successfully"));

    QueryBindableStructs();
}

void AMySceneStateManager::QueryBindableStructs()
{
    if (!LoadedBlueprint)
    {
        return;
    }

    // 遍历所有绑定函数
    LoadedBlueprint->ForEachBindingFunction(
        [](const FSceneStateBindingFunction& InFunction, const FPropertyBindingBinding& InBinding) -> bool
        {
            UE_LOG(LogTemp, Log, TEXT("Found binding function in binding"));
            return true; // 继续遍历
        }
    );
}
```

## 模块依赖

该插件包含 14 个模块，模块间依赖关系如下。使用者通常只需依赖核心运行时模块。

| 模块 | 用途 |
|---|---|
| `PropertyBinding` | UE 属性绑定框架，提供 `FPropertyBindingPath`、`FPropertyBindingDataView` 等基础类型 |
| `SceneStateTasks` | 任务执行框架，定义状态中可执行的任务基类 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> **注意**：该插件的 14 个模块之间存在内部依赖关系。如果你只需要在运行时访问状态机数据，依赖 `SceneState` 和 `SceneStateBinding` 即可。如果需要蓝图编辑功能，还需依赖 `SceneStateBlueprint`。

## 维护状态

### 近期更新

```
- 9d2e4cc30738 Motion Design Scene State: fixed issue where copying tasks/etc would not copy over the function values (only type).
- 0a35bd340336 Motion Design Scene State: fixed issue where state machine parameters, etc would not appear in the property binding menu for funcitons. Additionally fixed an issue where binding extensions wre not allocating function instances in execution.
- b660852deaec Motion Design Scene State: moved the generated class scene state data to its own struct to decouple compilers and executors from the generated class. This is done to allow to build unit tests without needing to deal with the generated class, and only use this template data struct.
```

### 维护评价

- **创建时间**：2025-04-22，非常新的插件（约 3 个月）
- **更新频率**：近期有持续的 bug 修复和架构重构，处于活跃开发阶段
- **维护状态**：🟢 **活跃开发中** — 最近的提交集中在修复属性绑定、任务复制等功能性 bug，以及为单元测试做架构准备（解耦编译器和执行器）
- **已知限制**：
  - 标记为 `IsBetaVersion: true`，API 可能发生变化
  - 分类为 Experimental，尚未正式发布
  - 部分 commit message 存在拼写错误（如 "funcitons"、"wre"），表明代码仍在快速迭代中
- **推荐程度**：⚠️ **谨慎使用** — 如果你在做 Motion Design / 虚拟制片项目且需要状态机管理，可以开始试用，但要做好 API 变化的准备。不建议在生产环境中依赖此插件的稳定 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SceneState)
- 官方文档：暂无

---

## 子模块概览

该插件包含 14 个模块，按功能可分为以下几组：

### 核心运行时

| 模块 | 职责 |
|---|---|
| `SceneState` | 状态机核心运行时，状态定义、执行和管理 |
| `SceneStateBinding` | 属性绑定系统运行时，管理状态与外部对象的属性绑定 |
| `SceneStateEvent` | 事件系统运行时，定义和触发状态转换事件 |
| `SceneStateTasks` | 任务系统运行时，定义状态中可执行的任务 |
| `SceneStateGameplay` | Gameplay 集成，将状态机与游戏逻辑连接 |

### 蓝图集成

| 模块 | 职责 |
|---|---|
| `SceneStateBlueprint` | 蓝图资产类型定义（`USceneStateBlueprint`、`USceneStateTaskBlueprint`） |
| `SceneStateBlueprintEditor` | 蓝图编辑器扩展，提供自定义蓝图编辑体验 |

### 图表系统

| 模块 | 职责 |
|---|---|
| `SceneStateMachineGraph` | 状态机可视化图表（节点和连线） |
| `SceneStateEventGraph` | 事件图表编辑器 |
| `SceneStateTransitionGraph` | 转换条件图表编辑器 |

### 编辑器工具

| 模块 | 职责 |
|---|---|
| `SceneStateEditor` | 通用编辑器工具和 UI |
| `SceneStateEventEditor` | 事件编辑器工具 |
| `SceneStateGameplayEditor` | Gameplay 集成的编辑器工具 |
| `SceneStateMachineEditor` | 状态机编辑器工具和自定义节点 |