# MutablePopulation

> Extend the Mutable plugin to support Population assets.

| 属性 | 值 |
|---|---|
| 中文名 | 人群生成 |
| 分类 | CustomizableObjects |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `CustomizableObjectPopulation` (Runtime), `CustomizableObjectPopulationEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation) | |

## 用途

**MutablePopulation** 是 **Mutable** 插件（自定义对象系统）的扩展，用于快速生成大量随机的、具备不同外观参数的 **自定义对象实例**。它解决了需要创建许多外观各异但结构相同的角色或物品（如 NPC 人群、装甲变体、植被变种）时的痛点——传统方式需要手动逐一实例化并设置参数，而该插件通过定义“人口类（PopulationClass）”和“人口（Population）”资产，基于概率约束自动随机采样并完善参数，从而批量生成实例。

插件内部使用多种采样器（BoolSampler、OptionSampler、FloatUniformSampler、FRangesSampler、FCurveSampler、ColorSampler 等）和约束系统（Constraint），使得生成的实例既丰富多样又满足设计者设定的概率偏好。

## 使用场景

- **开放世界 NPC 生成**：需要生成上千个不同服装、肤色、身形的角色，每个角色由 Mutable 定义参数化网格，使用该插件可一次性生成全部实例。
- **批量道具生成**：如武器、盔甲的随机外观变体，通过设定各类特征的权重分布快速创建变体库。
- **关卡环境填充**：随机生成不同样式的树木、石头、建筑部件，赋予场景自然变化。
- **游戏测试**：自动生成大量随机变体用于测试 Mutable 系统的性能或视觉效果稳定性。

## 蓝图用法

插件暴露了两个核心蓝图可调用函数，均位于 `UCustomizableObjectPopulation` 对象上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GeneratePopulation` | 为当前 Population 生成指定数量的新实例，返回生成所使用的种子值（出错返回 -1）。 | `UCustomizableObjectPopulation` |
| `RegeneratePopulation` | 使用指定种子重新生成实例，可用于恢复特定排列或调试。返回 false 表示出错。 | `UCustomizableObjectPopulation` |

### 使用示例（蓝图描述）

1. **准备入口数据**：在内容浏览器中创建 `CustomizableObjectPopulation` 资产，并设置其 `ClassWeights` 数组，添加引用已定义好的 `CustomizableObjectPopulationClass` 资产，并赋予各 Class 权重。
2. **生成实例**：使用节点 `GeneratePopulation`，输入 `Target`（Population 对象引用）、`NumInstancesToGenerate`（如 10），输出 `OutInstances` 数组和 `Return Value`（种子）。若返回值为 -1，表示资产无效（如缺少 Generator）。
3. **重新生成**：把之前生成的种子存入变量，调用 `RegeneratePopulation`，传入相同种子和实例数组，可恢复相同序列的结果。
4. **后续处理**：得到的 `UCustomizableObjectInstance` 数组可在运行时实例化为 Actor，或用于预览。

> 注意：`GeneratePopulation` 和 `RegeneratePopulation` 均为纯函数（Pure），不影响自身状态，多次调用可独立生成不同序列。

## C++ 用法

### 头文件引入

```cpp
#include "MuCOP/CustomizableObjectPopulation.h"
#include "MuCOP/CustomizableObjectPopulationClass.h"
#include "MuCOP/CustomizableObjectPopulationGenerator.h"
```

### 基本用法

```cpp
// 从现有资产加载 Population 和 PopulationClass
UCustomizableObjectPopulation* MyPopulation = LoadObject<UCustomizableObjectPopulation>(nullptr, TEXT("/Game/MyPopulations/MyPopulation.MyPopulation"));
if (!MyPopulation)
{
    return;
}

// 检查入口是否有效（所有 Class 都存在）
if (!MyPopulation->IsValidPopulation())
{
    UE_LOG(LogTemp, Error, TEXT("Population is invalid: missing classes."));
    return;
}

// 确保 Generator 已编译（在编辑器下必须手动编译）
#if WITH_EDITOR
if (!MyPopulation->HasGenerator())
{
    MyPopulation->CompilePopulation();
}
#endif

// 生成 50 个实例
TArray<UCustomizableObjectInstance*> Instances;
int32 Seed = MyPopulation->GeneratePopulation(Instances, 50);
if (Seed == -1)
{
    // 处理错误
}

// 使用实例（例如 SpawnActor，这里只演示）
for (UCustomizableObjectInstance* Instance : Instances)
{
    // 根据 Instance 的道具/角色生成对应 Actor
}

// 如果需要重新生成相同序列：
TArray<UCustomizableObjectInstance*> Regenerated;
bool bSuccess = MyPopulation->RegeneratePopulation(Seed, Regenerated, 50);
check(bSuccess);
```

**来源文件**：`Public/MuCOP/CustomizableObjectPopulation.h`

### 进阶用法

当需要自定义 Constraints 与 Samplers 时，可直接操作 `FCustomizableObjectPopulationCharacteristic` 和 `FCustomizableObjectPopulationConstraint` 结构体，并在 `CustomizableObjectPopulationClass` 的 `Characteristics` 数组中配置。例如：

```cpp
// 创建一个人口类，并添加约束
UCustomizableObjectPopulationClass* MyClass = NewObject<UCustomizableObjectPopulationClass>();
MyClass->Name = TEXT("NPC_Elf");
// 指定 CustomizableObject（参数化对象）
MyClass->CustomizableObject = LoadObject<UCustomizableObject>(nullptr, TEXT("/Game/Mutable/NPC_Elf.NPC_Elf"));

// 添加一个布尔型特征（如是否带帽子）
FCustomizableObjectPopulationCharacteristic Char;
Char.ParameterName = TEXT("HasHat");
FCustomizableObjectPopulationConstraint Constraint;
Constraint.Type = EPopulationConstraintType::BOOL;
Constraint.TrueWeight = 3;   // 75% 概率 True
Constraint.FalseWeight = 1;  // 25% 概率 False
Constraint.ConstraintWeight = 1;
Char.Constraints.Add(Constraint);
MyClass->Characteristics.Add(Char);

// 将 MyClass 加入 Population
MyPopulation->ClassWeights.Add({ MyClass, 5 }); // 权重 5
```

**来源说明**：对应 `CustomizableObjectPopulationConstraint.h` 和 `CustomizableObjectPopulationClass.h` 中的定义。

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，演示如何在运行时通过代码创建 Population 并生成实例。注意该示例假定 Mutable 插件已启用且相关资产已存在。

**CustomPopulationDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CustomPopulationDemo.generated.h"

UCLASS()
class ACustomPopulationDemo : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};
```

**CustomPopulationDemo.cpp**
```cpp
#include "CustomPopulationDemo.h"
#include "MuCOP/CustomizableObjectPopulation.h"
#include "MuCOP/CustomizableObjectPopulationClass.h"
#include "MuCOP/CustomizableObjectPopulationGenerator.h"
#include "MuCOP/CustomizableObjectInstance.h"   // Mutable 模块中的实例类

void ACustomPopulationDemo::BeginPlay()
{
    Super::BeginPlay();

    // 加载两个已存在的人口类资产
    UCustomizableObjectPopulationClass* ElfClass = LoadObject<UCustomizableObjectPopulationClass>(
        nullptr, TEXT("/Game/MyClasses/ElfClass.ElfClass"));
    UCustomizableObjectPopulationClass* OrcClass = LoadObject<UCustomizableObjectPopulationClass>(
        nullptr, TEXT("/Game/MyClasses/OrcClass.OrcClass"));
    if (!ElfClass || !OrcClass) return;

    // 创建人口资产（仅运行时创建，不会保存到磁盘）
    UCustomizableObjectPopulation* Population = NewObject<UCustomizableObjectPopulation>();
    Population->Name = TEXT("TempPopulation");

    // 设置两类权重：精灵权重 7，兽人权重 3（70% vs 30%）
    Population->ClassWeights.Add({ ElfClass, 7 });
    Population->ClassWeights.Add({ OrcClass, 3 });

    // 检查有效性并编译（编译需要编辑器上下文，此示例仅用于运行时测试演示原理）
    if (!Population->IsValidPopulation())
    {
        UE_LOG(LogTemp, Error, TEXT("Population is invalid, cannot generate."));
        return;
    }

    // 注意：运行时 CompilePopulation 不可用（仅在 WITH_EDITOR 下定义），
    // 因此必须预先烘焙好 Generator 或通过编辑器编译。
    // 此处假设资产已手动编译过（Population 具有 Generator）。
    if (!Population->HasGenerator())
    {
        UE_LOG(LogTemp, Warning, TEXT("Population has no generator, compile it in editor first."));
        return;
    }

    // 生成 20 个实例
    TArray<UCustomizableObjectInstance*> Instances;
    int32 Seed = Population->GeneratePopulation(Instances, 20);
    if (Seed == -1)
    {
        UE_LOG(LogTemp, Error, TEXT("GeneratePopulation failed."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Generated %d instances with seed %d"), Instances.Num(), Seed);

    // 实例的后续使用（例如生成蓝图 Actor）可根据项目需求自行实现
}
```

> 实际项目中，建议在编辑器下通过蓝图或 C++ 操作资产，而非运行时创建未编译的 Population。编译流程依赖于编辑器，因此运行时使用的 Population 资产应提前在编辑器内编译。

## 模块依赖

由于该模块为 Runtime 模块却依赖了 UnrealEd 等编辑器模块（可能是历史原因），在使用时需要额外注意。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能，如编译 Generator、缓存平台数据 |
| `DerivedDataCache` | 数据缓存，用于人口资源编译 |
| `EditorStyle` | 编辑器界面样式（可能用于某些编辑器相关功能） |
| `MessageLog` | 编译过程中的日志输出 |

其余标准依赖（Core、CoreUObject、Engine 等）已省略。

> **注意**：`CustomizableObjectPopulation` 虽然标记为 Runtime 类型，但依赖了编辑器模块。这意味着在打包的运行时游戏中使用时，部分功能（如 CompilePopulation）无法调用，且可能引发链接警告或错误。实际使用中建议将生成操作放在编辑器流程完成，运行时只读取已编译的 Generator 数据。

## 维护状态

### 近期更新

- 2025-06-10  bb3758b4  `SEditorViewport::MakeViewportToolbar() is deprecated.`  – 适配编辑器 API 废弃
- 2025-05-29  f5ac91eb  `Removing invalid appearances of U macros...`  – 清理宏定义
- 2025-04-29  13d19592  `[mutable population] Fixed random crash when using 3 or more mutable population classes...`  – 修复 3 个及以上人口类时的随机崩溃
- 2025-03-26  634dfda6  `[mutable] Changed the title of the tab of all CustomizableObject editors so...`  – 编辑器界面标题统一
- 2025-03-13  b059f7b4  `Fix trivial unreachable code warnings.`  – 初始提交，修复不可达代码警告

### 维护评价

| 维度 | 评价 |
|---|---|
| 创建时间 | 2025-03-13，距今约 6 个月 |
| 近期更新 | 有多次编译修复和崩溃修复，最近一次更新在 2025-06-10 |
| 活跃程度 | 活跃：最近 3 个月有实质性 commit（包括功能修复） |
| 已知问题 | 实验性插件，可能存在未覆盖的边缘情况；运行时无编辑器支持，编译需预先生成 |
| 推荐使用 | ✅ 若项目已使用 Mutable 插件，且需要批量生成变体，推荐启用。但需注意其实验性状态，建议在开发阶段充分测试。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MutablePopulation)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/Mutable/)（Mutable 总体文档，人口生成子内容）
- 测试用例：未在插件目录内提供独立的测试文件，可通过 Mutable 插件测试集（`Engine/Plugins/Experimental/Mutable/Tests/`）查找相关用例。