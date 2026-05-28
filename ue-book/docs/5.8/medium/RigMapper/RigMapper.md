# Rig Mapper

> A set of animation remapping features（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画曲线重映射器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、定义文件、图表编辑器） |
| 模块 | `RigMapper` (Runtime), `RigMapperEditor` (UncookedOnly), `RigMapperDeveloper` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper) | |

## 用途

RigMapper 是一个用于**动画曲线重映射**的实验性插件。它解决的核心问题是：如何将一组输入动画曲线（例如来自面部捕捉或旧版骨骼）通过一套复杂的、可配置的规则，重新映射为另一组输出动画曲线（例如目标游戏内角色的 Morph Targets 或骨骼旋转）。

插件提供了一套完整的工具链，从**定义文件**（通过 JSON 或在编辑器中可视化编辑）来描述映射规则，到**运行时处理器**高效地评估这些规则。它旨在处理复杂的、非线性的动画转换，支持多种映射特性（加权求和、逐段线性 SDK、数学运算等），并且可以**链接多个定义**以形成处理管道。

## 使用场景

- 你需要将 A 品牌的动作捕捉数据转换为你项目自定义角色的面部表情系统。
- 你有一套旧版本的动画资产，需要将其曲线映射到新版角色的骨骼和 Morph Target 上。
- 你需要在蓝图或 C++ 中，为动画蓝图的每个 Tick 执行一套复杂的、可配置的动画曲线运算。

## 蓝图用法

插件提供了核心资产 `URigMapperDefinition`（定义文件）和 `URigMapperLinkedDefinitions`（链接定义），以及在动画蓝图中使用的动画节点 `FAnimNode_RigMapper`。

### 核心资产与节点

| 节点/资产 | 说明 | 所在类 |
|---|---|---|
| `Load From Json File` | 从 JSON 文件加载映射定义。 | `URigMapperDefinition` |
| `Export As Json String` | 将当前定义导出为 JSON 字符串。 | `URigMapperDefinition` |
| `Validate` | 校验当前定义的有效性（输入/输出/特征引用）。 | `URigMapperDefinition` |
| `Bake Definitions` | 将链接的多个定义“烘焙”成一个单一的、优化的定义。 | `URigMapperLinkedDefinitions` |
| `Rig Mapper` (Anim Node) | 动画蓝图节点，用于在动画求值过程中执行曲线重映射。 | `FAnimNode_RigMapper` |

### 使用示例（蓝图描述）

1.  **创建定义资产**：在内容浏览器中右键 -> Animation -> Rig Mapper Definition。
2.  **配置定义**：双击打开资产编辑器，可以在此处导入 JSON 或手动添加输入/输出曲线及各类映射特征（加权求和、SDK 关键帧等）。
3.  **在动画蓝图中使用**：
    - 在动画图表中添加 `Rig Mapper` 节点。
    - 将 `Source Pose` 引脚连接到上游节点。
    - 在节点的 `Details` 面板中，将 `Definitions` 数组指向你创建的 `URigMapperDefinition` 资产。
    - 将节点的 `Result Pose` 连接到动画蓝图的输出。
4.  **动态控制**：可以通过 `Alpha` 属性控制映射结果的混合强度。

## C++ 用法

### 核心类

- `FacialRigMapping::FRigMapper`: 轻量级的运行时评估器，直接在 C++ 中操作。
- `FRigMapperProcessor`: 性能优化的批量评估器，适合动画系统。

### 头文件引入

```cpp
#include "RigMapper.h"
#include "RigMapperProcessor.h"
```

### 基本用法（直接评估）

```cpp
// 假设你已经有一个 URigMapperDefinition* Definition 对象
using namespace FacialRigMapping;

// 1. 创建评估器并加载定义
FRigMapper RigMapper;
if (RigMapper.LoadDefinition(Definition))
{
    // 2. 设置输入值 (可以通过索引或名称)
    RigMapper.SetDirectValue(FName(“EyeBlinkLeft”), 0.8f);
    RigMapper.SetDirectValue(1, 0.5f); // 通过索引

    // 3. 获取输出值
    TMap<FName, double> OutputValues = RigMapper.GetOutputValues();
    for (const auto& Pair : OutputValues)
    {
        UE_LOG(LogTemp, Log, TEXT(“Output %s: %f”), *Pair.Key.ToString(), Pair.Value);
    }
}
```
（来源：根据 `Public/RigMapper.h` 中 `FRigMapper` 类的接口推断）

### 进阶用法（批量评估与处理）

```cpp
// 使用 FRigMapperProcessor 进行批量、高性能的帧评估
// 适用于需要在 Tick 中处理大量曲线或链接多个定义的情况

TArray<URigMapperDefinition*> Definitions; // 你的定义列表
FRigMapperProcessor Processor(Definitions);

if (Processor.IsValid())
{
    // 准备输入数据（假设为单帧）
    TArray<FName> CurveNames = Processor.GetInputNames();
    FRigMapperProcessor::FPoseValues InputValues;
    InputValues.SetNum(CurveNames.Num());
    // ... 填充 InputValues ...

    FRigMapperProcessor::FPoseValues OutputValues;

    // 评估单帧
    if (Processor.EvaluateFrame(CurveNames, InputValues, OutputValues))
    {
        // OutputValues 中包含按 GetOutputNames() 顺序排列的结果
        // 将结果应用到动画 Pose Curves 上
    }
}
```
（来源：根据 `Public/RigMapperProcessor.h` 中 `FRigMapperProcessor` 类的接口推断）

## Demo 示例

以下是一个最小的 C++ 示例，展示如何加载定义并评估一帧数据。

**MyRigMapperComponent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RigMapper.h"
#include “MyRigMapperComponent.generated.h”

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyRigMapperComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyRigMapperComponent();

    UPROPERTY(EditAnywhere, Category = “Rig Mapper”)
    TObjectPtr<URigMapperDefinition> DefinitionAsset;

    UFUNCTION(BlueprintCallable, Category = “Rig Mapper”)
    void EvaluateAndPrintOutputs();

private:
    FacialRigMapping::FRigMapper RigMapper;
};
```

**MyRigMapperComponent.cpp**
```cpp
#include “MyRigMapperComponent.h”
#include “RigMapperDefinition.h”

UMyRigMapperComponent::UMyRigMapperComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyRigMapperComponent::EvaluateAndPrintOutputs()
{
    if (!DefinitionAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT(“No definition asset set.”));
        return;
    }

    // 1. 加载定义到评估器
    if (!RigMapper.LoadDefinition(DefinitionAsset))
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to load definition.”));
        return;
    }

    // 2. 设置一些示例输入值
    const TArray<FName>& InputNames = RigMapper.GetInputNames();
    if (InputNames.Num() > 0)
    {
        RigMapper.SetDirectValue(InputNames[0], 0.5f);
    }
    if (InputNames.Num() > 1)
    {
        RigMapper.SetDirectValue(InputNames[1], 1.0f);
    }

    // 3. 获取并打印输出
    TMap<FName, double> Outputs = RigMapper.GetOutputValues();
    UE_LOG(LogTemp, Log, TEXT(“Rig Mapper Outputs:”));
    for (const auto& Output : Outputs)
    {
        UE_LOG(LogTemp, Log, TEXT(“  %s: %f”), *Output.Key.ToString(), Output.Value);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供底层的 Rig 构建和评估框架。RigMapper 的评估器构建可能与之相关。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ab890466` | [RigMapper] Improved RigMapperDefinition logging and testing | 改进了定义的日志记录并增加了测试 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断到 float 产生警告的代码 |
| 2026-05-12 | `40287b95` | [RigMapper] Fixed broken automated tests, added missing automated tests, fixed a bug detected by upd | 修复了损坏的自动化测试，补充了缺失的测试，并修复了一个由更新发现的 Bug |
| 2026-05-12 | `edf81547` | [RigMapper] Made importing inputs/outputs from Control Rig optional in order to reduce clatter | 将从 Control Rig 导入输入/输出设为可选，以减少编辑器中的杂乱 |
| 2026-05-12 | `7268ff8e` | [RigMapper] Fixed a bug with comment nodes not fully enclosing selected rig mapper nodes and not tri | 修复了注释节点不能完全包围所选 RigMapper 节点以及相关触发逻辑的 Bug |

### 维护评价

- **创建时间**：插件于 2024 年 9 月创建，非常年轻（约 1 年）。
- **近期活跃度**：在 2026 年 5 月有多次连续提交，内容涉及 Bug 修复、测试完善和用户体验优化，表明**正在活跃维护中**。
- **实验性状态**：`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着它是一个**实验性功能**，API 可能会在未来版本中发生变化，不建议在核心生产流程中直接依赖。
- **推荐度**：**有条件推荐**。适合在实验项目或内部工具链中尝试，用于解决复杂的动画曲线重映射需求。由于其活跃的维护状态和清晰的代码结构，是一个值得关注的前沿功能。在生产环境中使用前需做好 API 稳定性的风险评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper)
- 官方文档：无（插件为实验性，文档URL为空）
- 测试用例：根据 Git 记录，存在自动化测试（路径通常位于 `Source/RigMapperDeveloper` 或 `Tests` 目录下），但具体路径未在提供信息中明确。