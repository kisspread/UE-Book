# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图模板、特性栈节点、编辑器资产） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimGraphUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0.1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 用途

UAF（Unreal Animation Framework）是一个实验性的下一代动画系统。**UAFAnimGraph** 提供定义、编辑和执行动画图的完整基础设施。

区别于传统 AnimBlueprint，UAF 动画图采用 **特性栈（Trait Stack）** 和 **RigVM** 组合模型。每个节点由一组有序的 Trait 构成，每个 Trait 提供特定的动画逻辑（如播放序列、混合、注入等），用户可通过蓝图或 C++ 动态增删排序。整个图在编辑器中使用 RigVM 编译为可执行字节码，实现高性能动画计算。

该插件解决的核心问题：
- 传统 AnimBlueprint 节点固定、扩展复杂 → UAF 允许组合 Trait 自由构建节点行为
- 动画图状态管理分散 → 统一通过 RigVM 编译和执行
- 编辑器内预览与运行时一致 → 内置资产工作区（Workspace Asset）支持

## 使用场景

- 开发需要复杂动画混合、状态切换、注入修改的交互系统（如角色动作、运动匹配）
- 希望以模块化 Trait 方式封装动画逻辑，实现跨项目复用
- 需要完全程序化构建动画图（蓝图或 C++ 动态生成节点与连接）
- 正在探索下一代动画管线，愿意使用实验性功能

## 蓝图用法

### 核心节点（蓝图函数 / 自定义节点）

| 节点 / 函数 | 说明 | 所在类 |
|---|---|---|
| `AddAnimationGraph` | 在 UAnimNextAnimationGraph 资产中添加一个动画图条目 | `UAnimNextAnimationGraphLibrary` |
| `AddTraitStruct` / `AddTraitByName` | 向现有节点堆栈添加一个 Trait（支持默认值） | `UAnimNextController` |
| `RemoveTraitByName` | 按实例名称从节点移除一个 Trait | `UAnimNextController` |
| `SwapTraitByName` | 用一个新类型 Trait 替换现有 Trait | `UAnimNextController` |
| `SetTraitPinIndex` | 移动 Trait 在堆栈中的顺序（视觉重排） | `UAnimNextController` |
| `K2Node_AnimNextPlayAnim` | 异步播放动画的蓝图节点（OnFinished 输出） | `UK2Node_AnimNextPlayAnim` |
| `K2Node_AnimNextInjection` | 注入外部动画逻辑的异步节点 | `UK2Node_AnimNextInjection` |

### 使用示例（蓝图描述）

1. **创建动画图资产**  
   - 在内容浏览器中右键 → 动画 → UAF → Animation Graph  
   - 打开资产编辑器，在“代码”视图中可用 `AddAnimationGraph` 节点（属于 `AnimNextAnimationGraph` 对象函数）创建一个新的动画图条目，指定名称。

2. **添加 Sequence Player 节点**  
   - 在图编辑器中右键 → UAF → Sequence Player  
   - 选中节点 → 在细节面板中设置 `AnimSequence` 引用  
   - 若要动态修改 Trait，可使用 `AddTraitByName` 在运行时向节点插入 BlendSmoother 等 Trait。

3. **使用 Play Anim 节点**  
   - 在蓝图（Level Blueprint 或 Actor）中放置 `Play AnimNext Animation` 节点（来自 `K2Node_AnimNextPlayAnim`）  
   - 连接 `Animation Graph` 资产引用，执行时异步播放，并在 `On Finished` 执行后续逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNextController.h"
#include "AnimNextAnimationGraph_EditorData.h"
#include "AnimGraphUncookedOnlyUtils.h"
#include "Templates/UAFGraphNodeTemplate.h"
```

### 基本用法：创建简单动画图

以下示例演示如何通过 C++ 在编辑器脚本中创建一个包含 Sequence Player 节点的动画图（源自测试用例 `FAnimationAnimNextEditorTest_GraphAddTrait`）。

```cpp
// 来源：Engine/Plugins/Experimental/UAF/UAFAnimGraph/Source/UAFAnimGraphTestSuite/Private/... (测试用例)
#include "AnimNextController.h"
#include "AnimNextAnimationGraph_EditorData.h"
#include "AnimNextAnimationGraphEntry.h"
#include "Traits/SequencePlayerTraitData.h"

void CreateSimpleAnimationGraph(UAnimNextAnimationGraph* InGraph)
{
    // 1. 获取编辑器数据
    UAnimNextAnimationGraph_EditorData* EditorData = Cast<UAnimNextAnimationGraph_EditorData>(
        InGraph->GetEditorData());
    if (!EditorData) return;

    // 2. 添加一个动画图条目
    UAnimNextAnimationGraphEntry* Entry = EditorData->AddAnimationGraph(NAME_None, true, true);
    if (!Entry) return;

    // 3. 获取控制器
    UAnimNextController* Controller = Cast<UAnimNextController>(Entry->GetRigVMGraph()->GetController());
    Controller->OpenUndoBracket(TEXT("CreateGraph"));

    // 4. 添加 Sequence Player 节点（通过模板路径）
    const FString NodePath = TEXT("Sequencer Player"); // 实际使用模板类名
    URigVMUnitNode* Node = Controller->AddUnitNodeByScriptStruct(
        FSequencePlayerData::StaticStruct(),
        FRigVMPinInfoArray(),
        TEXT("Execute"), FVector2D(0,0));
    
    // 5. 设置动画序列 Pin
    Controller->SetPinDefaultValue(
        Node->FindPin(TEXT("AnimNextSequencePlayerTraitSharedData.AnimSequence")),
        TEXT("/Game/Animations/MySequence.MySequence"),
        true, true, true, true);

    Controller->CloseUndoBracket();
}
```

### 进阶用法：动态管理 Trait 堆栈

```cpp
// 假设已有一个 TraitStack 节点（UAnimNextTraitStackUnitNode*）
UAnimNextController* Controller = ...;
URigVMUnitNode* TraitStackNode = ...;

// 添加 BlendByBool Trait（使用默认值）
FName TraitInstanceName = Controller->AddTraitByName(
    TraitStackNode->GetFName(),
    GET_MEMBER_NAME_CHECKED(FAnimNextBlendByBoolTraitSharedData, StaticStruct()->GetFName()), // 实际类型名
    0, TEXT(""), true, true);

// 交换为 BlendSmoother Trait
Controller->SwapTraitByName(
    TraitStackNode->GetFName(),
    TraitInstanceName,
    0,
    GET_MEMBER_NAME_CHECKED(FAnimNextBlendSmootherTraitSharedData, StaticStruct()->GetFName()),
    TEXT(""), true, true);

// 删除 Trait
Controller->RemoveTraitByName(TraitStackNode->GetFName(), TraitInstanceName, true, true);
```

## Demo 示例

以下是一个完整的最小示例，创建一个 UAnimNextAnimationGraph 资产并在其中添加一个简单的动画图条目。（需要依赖 UAF 插件和 UAFAnimGraph 模块）

**AnimGraphDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNextAnimationGraph.h"
#include "AnimGraphDemo.generated.h"

UCLASS(BlueprintType)
class UAnimGraphDemo : public UAnimNextAnimationGraph
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void InitializeDemo();
};
```

**AnimGraphDemo.cpp**
```cpp
#include "AnimGraphDemo.h"
#include "AnimNextAnimationGraph_EditorData.h"
#include "AnimNextController.h"
#include "AnimNextAnimationGraphEntry.h"

void UAnimGraphDemo::InitializeDemo()
{
    // 获取 EditorData（编辑器环境下才有效）
    UAnimNextAnimationGraph_EditorData* EditorData = Cast<UAnimNextAnimationGraph_EditorData>(
        GetEditorData());
    if (!EditorData) return;

    // 添加一个名为 "Demo" 的动画图
    UAnimNextAnimationGraphEntry* Entry = EditorData->AddAnimationGraph(
        FName("Demo"), true, false);
    if (!Entry) return;

    UAnimNextController* Controller = Cast<UAnimNextController>(
        Entry->GetRigVMGraph()->GetController());
    if (!Controller) return;

    // 添加一个 Sequence Player 节点
    Controller->OpenUndoBracket(TEXT("SetupDemo"));
    URigVMUnitNode* SeqNode = Controller->AddUnitNode(
        FSequencePlayerData::StaticStruct(),
        TEXT("Execute"), FVector2D(100, 100));
    if (SeqNode)
    {
        // 设置动画序列路径（示例硬编码）
        Controller->SetPinDefaultValue(
            SeqNode->FindPin(TEXT("AnimNextSequencePlayerTraitSharedData.AnimSequence")),
            TEXT("AnimSequence'/Game/TestAnim.TestAnim'"),
            true, true, true, true);
    }
    Controller->CloseUndoBracket();
}
```

## 模块依赖

基于 `UAFAnimGraphUncookedOnly` 模块（隐含通过所有模块传递的公共依赖），以下列出非标准依赖：

| 模块 | 用途 |
|---|---|
| `UAF` | 提供核心动画框架类型（Trait、参数类型、执行上下文） |
| `AnimNext` | 提供动画图编辑数据基类、RigVM 集成 |
| `RigVM` | 提供图模型、字节码编译与执行 |
| `AnimGraphRuntime` | 动画图运行时序列化与执行（在 Editor 模式下同样需要） |
| `AnimNextUncookedOnly` | 提供资产工作区和编辑器导出基础 |

**被省略的常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UnrealEd, UMG, InputCore, DeveloperSettings, EditorStyle, Projects, PropertyEditor 等。

## 维护状态

### 近期更新

| 日期 | 哈希 | 说明 |
|---|---|---|
| 2025-10-01 | 6f23619b | 将拖放操作中 UEdGraphSchema 资产的引用过滤移动到各具体实现类中 |
| 2025-09-03 | bb48edd8 | 避免在编辑器退出时访问无效内存 |
| 2025-09-03 | bc59af4e | 避免在旧版 UAF 内容上打开上下文菜单时发生崩溃 |
| 2025-09-02 | 78089693 | 为 UAF 姿势求值添加作用域命名事件 |
| 2025-08-29 | 3663a91d | 修复 UAF RigVM 重写变量资产持久化问题 |

### 维护评价

- **创建时间**：2025-08-29（不足 1 年，完全新）
- **近期更新**：最近一个月内有多次实质性更新（功能改进、崩溃修复、资产持久化）
- **活跃程度**：活跃维护中，近期提交涉及功能开发与稳定性修复
- **已知问题**：存在 Legacy 内容兼容性问题（见 2025-09-03 修复），实验性标志警告可能存在 API 变动
- **推荐使用**：适合对新兴动画框架有探索需求的团队；不建议用于生产级项目，因还在快速迭代中

## 相关链接

- [源码（Plugin 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Source/UAFAnimGraphTestSuite)