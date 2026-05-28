# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 选择器表， 代理表） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套数据驱动的资产查找系统，主要用于在运行时动态选择和实例化资产（如动画蒙太奇、蓝图、材质等）。其核心思想是将选择逻辑从代码中抽离，以数据表的形式进行配置。

它主要由两部分组成：
1.  **代理表 (Proxy Table)**：一个数据资产，充当一个查找表。它定义了如何将一组输入（如游戏标签、枚举值、属性值）映射到一个输出资产。
2.  **选择器 (Chooser)**：另一个数据资产，用于定义查询条件和如何使用代理表。选择器可以包含多个代理表，并根据输入参数评估哪一个代理表的结果应当被使用。

在蓝图中，可以通过专门的节点（如 `Evaluate Proxy`）来执行选择器，传入上下文信息，然后获得一个动态选择的资产引用。这解决了在蓝图或C++中硬编码资产引用导致逻辑僵化、难以维护和扩展的问题。

## 使用场景

- 你需要根据玩家状态（如是否受伤、是否潜行）动态切换动画蒙太奇。
- 你需要根据游戏环境（如天气、时间）选择不同的材质或粒子效果。
- 你需要实现一个上下文敏感的对话系统，根据对话者和玩家关系选择不同的对话资产。
- 你希望美术或设计师能够在不修改代码的情况下，通过配置数据表来调整游戏内容的表现。

## 蓝图用法

该插件提供了两个核心的蓝图节点，均位于 `Proxy` 类别下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Proxy` | (旧版) 评估一个代理资产，基于当前上下文获取一个输出资产。 | `UK2Node_EvaluateProxy` |
| `Evaluate Proxy 2` | (新版) 功能增强的代理评估节点，支持传入多个输入对象和结构体，并返回多个结果。 | `UK2Node_EvaluateProxy2` |

### 使用示例（蓝图描述）

1.  **创建代理资产**：在内容浏览器中右键，选择 `Animation -> Chooser -> Proxy Table` 创建一个新的代理表资产。打开它，添加条目，将输入条件（如一个 `GameplayTag`）映射到对应的输出资产（如一个动画蒙太奇）。
2.  **创建选择器资产**：同样创建一个 `Chooser` 资产。在其中添加一个或多个代理表引用。
3.  **在蓝图中调用**：
    - 打开你的蓝图（如角色蓝图）。
    - 添加一个 `Evaluate Proxy 2` 节点。
    - 将创建好的 `Chooser` 资产或 `Proxy Table` 资产连接到节点的 `Proxy` 输入引脚。
    - 根据你代理表中设置的输入条件类型，连接相应的输入数据。例如，如果你的代理表基于 `GameplayTag` 查询，则将一个 `GameplayTag` 变量连接到 `Context` 引脚。
    - 节点的 `Result` 引脚将输出动态选择的资产。你可以将这个结果直接用于播放蒙太奇、生成Actor等后续操作。

## C++ 用法

该插件主要面向蓝图工作流，但核心的代理评估逻辑也暴露了C++接口。

### 头文件引入

```cpp
#include "Chooser.h"
#include "ProxyTable/ProxyTable.h"
```

### 基本用法

```cpp
// 假设你已经拥有一个有效的代理表资产指针：UProxyTable* MyProxyTable
// 以及一个用于查询的上下文结构体，例如 FGameplayTagQueryContext
FGameplayTagQueryContext QueryContext;
QueryContext.GameplayTag = FGameplayTag::RequestGameplayTag(FName(“Character.State.Walking”));

// 使用代理表进行评估
UObject* ResultObject = nullptr;
bool bSuccess = MyProxyTable->Evaluate(QueryContext, ResultObject);

if (bSuccess && ResultObject)
{
    // 使用动态选择到的资产，例如转换为动画蒙太奇
    UAnimMontage* SelectedMontage = Cast<UAnimMontage>(ResultObject);
    if (SelectedMontage)
    {
        // 播放动画
    }
}
```

### 进阶用法

新版节点 `Evaluate Proxy 2` 支持更复杂的查询，其对应的C++接口通常涉及更丰富的上下文结构体和可能返回结构体数据。用法模式类似，但需要构造更复杂的查询上下文，并可能处理结构体输出。

## Demo 示例

以下是一个简化的C++示例，演示如何定义一个查询结构体并使用代理表进行评估。

**MyGameTypes.h**
```cpp
#pragma once
#include "GameplayTagContainer.h"
#include "MyGameTypes.generated.h"

USTRUCT(BlueprintType)
struct FMyCharacterContext
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    FGameplayTag CharacterState;

    UPROPERTY(BlueprintReadWrite)
    bool bIsInCombat;
};
```

**MyAnimInstance.cpp**
```cpp
#include "MyAnimInstance.h"
#include "MyGameTypes.h"
#include "ProxyTable/ProxyTable.h"

void UMyAnimInstance::UpdateAnimation()
{
    if (UProxyTable* AnimProxyTable = GetAnimProxyTable())
    {
        // 构建查询上下文
        FMyCharacterContext Context;
        Context.CharacterState = GetCharacterStateTag();
        Context.bIsInCombat = IsInCombat();

        // 执行评估
        UObject* AnimAsset = nullptr;
        if (AnimProxyTable->Evaluate(Context, AnimAsset))
        {
            UAnimMontage* MontageToPlay = Cast<UAnimMontage>(AnimAsset);
            if (MontageToPlay && !Montage_IsPlaying(MontageToPlay))
            {
                Montage_Play(MontageToPlay);
            }
        }
    }
}
```

## 模块依赖

`ProxyTableUncooked` 模块（以及其他Uncooked模块）主要负责编辑器数据验证和序列化，其内部依赖未完全展示。根据插件用途和 `.uplugin` 依赖 `GameplayTagsEditor` 推断，使用者的模块可能需要以下依赖：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 处理基于GameplayTag的查询，这是选择器/代理表常见的查询维度。 |
| 动画相关模块 | 如 `AnimGraphRuntime`，取决于最终选择的资产类型。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 清理构建配置，将内部头文件从公共范围移出，改善模块封装性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下产生的双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为选择器的属性访问添加性能分析标记，便于性能调试。 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复在重命名原生上下文类型后，选择器编辑器出现的空指针崩溃。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | （关联更新）内容浏览器新增了“添加数据菜单”功能，可能与选择器资产创建入口相关。 |

### 维护评价

- **创建时间**：该插件于2024年9月从实验性文件夹移出，表明其功能已趋于稳定。
- **近期更新**：最近3个月内有多次提交，包括功能增强（性能标记）、问题修复（崩溃、警告）和代码重构（头文件管理），显示插件处于**活跃维护**状态。
- **活跃度**：高频次的近期更新表明 Epic 正在持续改进和优化该插件。
- **推荐使用**：是。作为一个相对较新且持续维护的官方动画工具链组件，它适合在新项目中采用，以实现灵活、数据驱动的资产选择逻辑。由于默认未启用，需要在项目的插件设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [官方文档](https://epicgames.com) （.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser/Tests) （推断路径）