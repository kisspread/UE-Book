# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 动态资产选择器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一种数据驱动的方法，用于在运行时根据一组规则或上下文条件，动态地选择并返回资产（如动画蒙太奇、音效、材质等）。它解决了传统方式中需要编写大量硬编码引用或复杂蓝图逻辑来切换资产的问题。

其核心概念包括：
- **Chooser Table**：一个数据表，定义了输入条件（如 GameplayTag、属性值）到输出资产（如动画）的映射规则。它类似于一个可由代码或蓝图查询的“决策表”。
- **Proxy Table & Proxy Asset**：用于创建资产的间接引用。`ProxyAsset` 是一个唯一的占位符标识，而 `ProxyTable` 则将这个标识映射到实际的资产实例。这使得可以在运行时或根据上下文轻松替换整个资产集合（如不同角色的动画集）。

该插件旨在提升动画系统和内容管线的灵活性与可维护性，尤其适合需要根据角色状态、角色类型或游戏进度动态切换内容的项目。

## 使用场景

- **动画蓝图集成**：在动画蓝图中，根据角色当前的 `GameplayTag` 或其他状态属性，通过 Chooser Table 动态选择要播放的动画蒙太奇或动画序列。
- **角色/皮肤切换**：使用 Proxy Table，为不同角色、皮肤或装备定义不同的视觉资产（如粒子特效、材质）。通过切换 Proxy Table 实例，可以一键更改角色的所有视觉表现。
- **配置化游戏内容**：将游戏中的内容（如任务对话、音效、UI 图标）的选取逻辑从代码中剥离，放入 Chooser Table 数据资产中，方便策划调整而无需重新编译代码。
- **模块化资产管理**：通过 `UProxyAsset` 作为模块间的接口引用资产，底层实现（`UProxyTable`）可以独立替换，实现逻辑与资产的解耦。

## 蓝图用法

核心蓝图函数由 `UProxyTableFunctionLibrary` 提供，可在动画蓝图或任何蓝图上下文中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateProxyAsset` | 根据提供的 `ProxyAsset` 和上下文对象，在关联的 `ProxyTable` 中查找并返回解析后的目标 `UObject`。 | `UProxyTableFunctionLibrary` |
| `MakeLookupProxy` | 创建一个 `FLookupProxy` 结构体实例，用于在 Chooser Table 的“对象选择器”列中指定一个 `ProxyAsset` 作为输出。 | `UProxyTableFunctionLibrary` |
| `MakeLookupProxyWithOverrideTable` | 同上，但允许显式指定一个覆盖用的 `ProxyTable`，忽略 `ProxyAsset` 自身关联的表。 | `UProxyTableFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **资产准备**：
    - 创建 `UProxyAsset`（例如命名为 `PA_AnimationAttack`）。
    - 创建 `UProxyTable`（例如命名为 `PT_WarriorAnimations`），在其中将 `PA_AnimationAttack` 映射到战士的攻击动画蒙太奇。
    - 同理，创建另一个 `PT_MageAnimations` 表，将同一个 `PA_AnimationAttack` 映射到法师的攻击动画。

2.  **在动画蓝图中使用**：
    - 在动画蓝图事件图表中，获取当前角色的“职业”信息。
    - 根据职业选择对应的 `ProxyTable`。
    - 调用 `EvaluateProxyAsset` 节点，传入 `PA_AnimationAttack`、选定的 `ProxyTable` 以及上下文对象（如 `self`）。
    - 将返回的动画蒙太奇资产连接到 `Play Montage` 节点，实现动态选择。

3.  **在 Chooser Table 中使用**：
    - 在 Chooser Table 编辑器中，为某一行的输出列添加一个 `FLookupProxy`。
    - 将其 `Proxy` 属性设置为 `PA_AnimationAttack`。
    - 当该行被选中时，系统会自动通过 `ProxyAsset` 和关联的 `ProxyTable` 解析出最终资产。

## C++ 用法

### 头文件引入

```cpp
#include "ProxyTable/ProxyAsset.h"
#include "ProxyTable/ProxyTable.h"
#include "ProxyTable/ProxyTableFunctionLibrary.h"
// 通常还需要 Chooser 模块的头文件
#include "Chooser/Chooser.h"
```

### 基本用法

以下代码演示了如何程序化地求值一个 Proxy Asset。

```cpp
// 假设已拥有以下对象指针：
UProxyAsset* MyProxyAsset = ...; // 已创建的代理资产
UProxyTable* MyProxyTable = ...; // 包含实际映射的代理表
UObject* ContextObject = ...;    // 提供上下文（如拥有此动画蓝图的 Actor）

// 构建求值上下文 (此结构体可能需要从 Chooser 模块获取)
FChooserEvaluationContext Context;
// ... 可能需要向 Context 添加属性

// 方法1：直接使用函数库（蓝图也用这个）
UObject* ResultObject = UProxyTableFunctionLibrary::EvaluateProxyAsset(ContextObject, MyProxyAsset, UObject::StaticClass());

// 方法2：通过 ProxyAsset 自身的方法
UObject* ResultObject2 = MyProxyAsset->FindProxyObject(Context);

// 方法3：如果知道 ProxyAsset 的 GUID（通常在编辑器数据中保存）
const FGuid& ProxyGuid = MyProxyAsset->Guid;
UObject* ResultObject3 = MyProxyTable->FindProxyObject(ProxyGuid, Context);
```
**注意**：`FChooserEvaluationContext` 的具体构造和属性绑定是 Chooser 插件的核心复杂部分，通常由动画蓝图或 Chooser 节点自动处理。

### 进阶用法

当需要处理多个可能结果或软引用时，可以使用迭代器回调。

```cpp
MyProxyTable->FindProxyObjectMulti(ProxyGuid, Context, [](UObject* Object) -> FObjectChooserBase::EIteratorStatus
{
    if (Object)
    {
        UE_LOG(LogTemp, Log, TEXT("Found proxy result: %s"), *Object->GetName());
        // 返回 EIteratorStatus::Continue 继续查找下一个，或 Stop 停止
        return FObjectChooserBase::EIteratorStatus::Continue;
    }
    return FObjectChooserBase::EIteratorStatus::Stop;
});
```

## Demo 示例

**需求**：创建一个 Actor 组件，该组件持有一个 `ProxyAsset` 引用，并提供一个函数来获取当前对应的动画资产。

### ProxyAssetDemoComponent.h
```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "ProxyAssetDemoComponent.generated.h"

class UProxyAsset;
class UAnimMontage;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UProxyAssetDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UProxyAssetDemoComponent();

    // 蓝图中可设置的代理资产引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
    TObjectPtr<UProxyAsset> AttackAnimationProxy;

    // 获取当前代理资产对应的动画蒙太奇
    UFUNCTION(BlueprintCallable, Category = "Animation")
    UAnimMontage* GetAttackMontage() const;

protected:
    virtual void BeginPlay() override;
};
```

### ProxyAssetDemoComponent.cpp
```cpp
#include "ProxyAssetDemoComponent.h"
#include "ProxyTable/ProxyAsset.h"
#include "Animation/AnimMontage.h"

UProxyAssetDemoComponent::UProxyAssetDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UProxyAssetDemoComponent::BeginPlay()
{
    Super::BeginPlay();
    // 可以在BeginPlay中验证ProxyAsset是否有效
    if (!AttackAnimationProxy)
    {
        UE_LOG(LogTemp, Warning, TEXT("ProxyAssetDemoComponent: AttackAnimationProxy is not set!"));
    }
}

UAnimMontage* UProxyAssetDemoComponent::GetAttackMontage() const
{
    if (!AttackAnimationProxy)
    {
        return nullptr;
    }

    // 构建一个简单的求值上下文，实际项目中可能需要填充更多数据
    FChooserEvaluationContext Context;

    // 使用ProxyAsset自身的函数进行解析
    UObject* Result = AttackAnimationProxy->FindProxyObject(Context);

    // 安全转换为AnimMontage
    return Cast<UAnimMontage>(Result);
}
```

## 模块依赖

使用 Chooser 插件，你的项目模块需要在 `.Build.cs` 文件中添加对以下模块的依赖：

| 模块 | 用途 |
|---|---|
| `Chooser` | 核心 Chooser Table 逻辑和运行时求值。 |
| `ProxyTable` | Proxy Table 和 Proxy Asset 的核心实现。 |

根据你使用的功能（编辑器、非烘焙逻辑），可能还需要：
- `ChooserEditor` / `ProxyTableEditor`：如果你的模块需要在编辑器中与 Chooser/ProxyTable 资产交互。
- `ChooserUncooked` / `ProxyTableUncooked`：如果你的模块需要在未烘焙（编辑器）环境下处理这些资产。

**注意**：由于这些模块本身是 Chooser 插件的一部分，当你的项目启用了 Chooser 插件后，这些模块会自动加载。你只需要在 `Build.cs` 中声明对它们的依赖即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 重构头文件，将内部头文件移出公共访问范围，提升模块封装性。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量转换为浮点数时产生的编译器警告。 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 属性访问添加性能分析标签，便于性能调试。 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复在原生上下文类型重命名后，编辑器中可能出现的空指针崩溃。 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | （属于引擎其他改动，但影响插件集成）内容浏览器新增“添加菜单数据”功能。 |

### 维护评价

- **活跃维护**：Chooser 插件自 2024 年 9 月从 Experimental 文件夹正式移出后，一直处于积极维护状态。最近的提交集中在 2026 年 4-5 月，修复了编译警告、崩溃和性能分析支持。
- **推荐使用**：该插件提供了强大的动态资产选择能力，尤其适合中大型动画驱动型项目。其数据驱动的特性符合现代游戏开发最佳实践。
- **注意事项**：
    1.  插件默认**未启用** (`EnabledByDefault: false`)，需在项目设置中手动启用。
    2.  核心类（如 `UProxyTable`, `UProxyAsset`）仍标记为 `Experimental`，意味着其 API 在未来版本中可能会发生变化。
    3.  概念相对复杂（Chooser Table， Proxy Table），需要团队策划和程序共同学习理解。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser/Tests)