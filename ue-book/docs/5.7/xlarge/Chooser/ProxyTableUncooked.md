# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 插件提供了一套**数据驱动的动态资产选择系统**，由两个核心概念组成：

1. **Chooser Table（选择器表）**：一种表格型数据资产，每一行定义一组输入条件和对应的输出结果。运行时根据上下文参数匹配条件，返回最合适的资产。类似于"决策表"或"查找表"，将原本需要大量 `if-else` 或 `switch-case` 的选择逻辑转化为可视化表格。

2. **Proxy Table（代理表）**：一种间接引用机制，通过代理对象引用实际资产。运行时可以通过代理表动态替换资产，而无需修改引用方代码。这实现了资产引用的解耦，特别适合需要热插拔资产的场景。

**为什么存在？** 在动画系统中，角色可能需要根据多种上下文条件（移动速度、方向、武器类型、姿态等）选择不同的动画资产。传统做法需要编写大量条件分支代码，难以维护和扩展。Chooser 将这些逻辑抽象为数据表格，设计师可以直接在编辑器中配置，无需程序员介入。

## 使用场景

- 你需要根据角色状态（速度、方向、装备等）动态选择动画蒙太奇 → 用 Chooser Table
- 你需要在运行时动态替换角色的动画资产（如换装系统） → 用 Proxy Table
- 你有一组复杂的条件选择逻辑，希望用可视化表格而非代码管理 → 用 Chooser Table
- 你需要在不修改引用方的情况下热插拔资产 → 用 Proxy Table
- 你在做动画系统，需要根据 Gameplay 上下文选择 Blend Space 或 AnimMontage → 用 Chooser + Proxy Table 组合

## 模块结构

本插件包含 6 个模块，分为 Chooser 和 ProxyTable 两组，每组各含 Runtime / Editor / UncookedOnly 三个模块：

| 模块 | 职责 |
|---|---|
| `Chooser` | 核心运行时：Chooser Table 数据资产定义、求值逻辑 |
| `ChooserEditor` | 编辑器：Chooser Table 的自定义资产编辑器和属性面板 |
| `ChooserUncooked` | 未打包支持：序列化、导入导出等仅在开发时使用的功能 |
| `ProxyTable` | 核心运行时：Proxy Table 数据资产定义、代理解析逻辑 |
| `ProxyTableEditor` | 编辑器：Proxy Table 的自定义资产编辑器和属性面板 |
| `ProxyTableUncooked` | 未打包支持：Proxy Table 的序列化和开发时功能 |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Evaluate Chooser` | 根据上下文求值 Chooser Table，返回匹配的资产 | `UChooserTable` |
| `Evaluate Proxy` | 通过 Proxy Table 解析并返回实际资产引用 | `UProxyTable` |
| `Evaluate Chooser (All Results)` | 求值 Chooser Table，返回所有匹配结果的数组 | `UChooserTable` |
| `Evaluate Proxy (All Results)` | 求值 Proxy Table，返回所有匹配结果的数组 | `UProxyTable` |

### 使用示例

**Chooser Table 基本用法：**

1. 在内容浏览器中右键 → Animation → Chooser Table，创建一个 Chooser Table 资产
2. 打开编辑器，定义输入列（如 GameplayTag、Float、Bool 等类型）和输出列（如 AnimMontage 资产引用）
3. 添加行，每行设置输入条件和对应的输出资产
4. 在蓝图中使用 `Evaluate Chooser` 节点：
   - 连接 Chooser Table 资产引用
   - 构建 `ChooserEvaluationContext`，填入当前上下文参数（如角色速度、方向等）
   - 输出即为匹配的资产对象

**Proxy Table 基本用法：**

1. 创建 Proxy Table 资产，定义代理条目（每个条目关联一个实际资产）
2. 在蓝图中使用 `Evaluate Proxy` 节点：
   - 连接 Proxy Table 资产引用
   - 指定要解析的代理键
   - 输出为实际的资产对象

**组合使用：**

Chooser Table 的输出列可以是 Proxy Table 引用，实现两层间接：Chooser 根据条件选择 Proxy → Proxy 解析为实际资产。这样可以在不修改 Chooser 逻辑的情况下，通过替换 Proxy Table 中的资产来热更新内容。

## C++ 用法

### 头文件引入

```cpp
#include "Chooser.h"
#include "ChooserPropertyAccess.h"
#include "ProxyTable.h"
```

### 基本用法

**求值 Chooser Table：**

```cpp
// 来源: Engine/Plugins/Chooser/Source/Chooser/

#include "Chooser.h"
#include "ChooserPropertyAccess.h"

// 创建求值上下文
FChooserEvaluationContext Context;

// 添加输入参数（根据 Chooser Table 定义的列类型）
Context.AddInputParam(FChooserInputBool(bIsInCombat));
Context.AddInputParam(FChooserInputFloat(MovementSpeed));
Context.AddInputParam(FChooserInputGameplayTag(CurrentState));

// 求值 Chooser Table
UObject* Result = nullptr;
if (ChooserTable)
{
    Result = ChooserTable->Evaluate(Context);
}

// 使用结果（如 AnimMontage）
UAnimMontage* SelectedMontage = Cast<UAnimMontage>(Result);
if (SelectedMontage)
{
    // 播放选中的蒙太奇
}
```

**求值 Proxy Table：**

```cpp
#include "ProxyTable.h"

// 通过 Proxy Table 解析实际资产
UObject* ActualAsset = nullptr;
if (ProxyTable)
{
    ActualAsset = ProxyTable->FindProxy(ProxyKey);
}
```

### 进阶用法

**获取所有匹配结果：**

```cpp
#include "Chooser.h"

FChooserEvaluationContext Context;
Context.AddInputParam(FChooserInputFloat(Speed));

// 获取所有匹配的行结果
TArray<UObject*> AllResults;
ChooserTable->EvaluateAll(Context, AllResults);

for (UObject* Result : AllResults)
{
    // 处理每个匹配结果
}
```

**自定义属性访问器：**

Chooser 系统支持通过属性访问器（Property Access）从对象上自动读取输入参数，无需手动构建 Context：

```cpp
#include "ChooserPropertyAccess.h"

// Chooser Table 可以配置属性路径，自动从 ContextObject 读取值
FChooserEvaluationContext Context;
Context.AddObjectParam(MyCharacter);  // 提供属性读取的源对象

// Chooser Table 中配置的属性路径会自动从 MyCharacter 上读取
UObject* Result = ChooserTable->Evaluate(Context);
```

## Demo 示例

### ChooserTable 使用示例

```cpp
// MyCharacterChooser.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacterChooser.generated.h"

class UChooserTable;
class UAnimMontage;

UCLASS()
class AMyCharacterChooser : public ACharacter
{
    GENERATED_BODY()

public:
    // 在编辑器中指定 Chooser Table 资产
    UPROPERTY(EditAnywhere, Category = "Animation")
    TObjectPtr<UChooserTable> AnimationChooser;

    // 根据当前状态选择并播放动画
    UFUNCTION(BlueprintCallable, Category = "Animation")
    void PlayContextualAnimation();
};
```

```cpp
// MyCharacterChooser.cpp
#include "MyCharacterChooser.h"
#include "Chooser.h"
#include "ChooserPropertyAccess.h"

void AMyCharacterChooser::PlayContextualAnimation()
{
    if (!AnimationChooser)
    {
        return;
    }

    // 构建求值上下文
    FChooserEvaluationContext Context;

    // 添加上下文参数
    const float Speed = GetVelocity().Size();
    Context.AddInputParam(FChooserInputFloat(Speed));

    const bool bIsFalling = GetMovementComponent()->IsFalling();
    Context.AddInputParam(FChooserInputBool(bIsFalling));

    // 求值获取动画资产
    UObject* Result = AnimationChooser->Evaluate(Context);

    UAnimMontage* Montage = Cast<UAnimMontage>(Result);
    if (Montage)
    {
        PlayAnimMontage(Montage);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | Chooser Table 支持 GameplayTag 类型的输入列 |
| `PropertyAccess` | 属性访问器系统，用于从对象上自动读取输入参数 |
| `StructUtils` | 结构体工具，用于 Chooser 内部数据处理 |

## 维护状态

### 近期更新

```
- 87bed3a038da Fix for BP compile errors with EvaluateChooser and EvaluateProxy when using Class outputs, and "All Results" Array output mode
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 365a11c5b937 [UObject/General] - Cleanup code and convert to the new ConditionalPreload function - Fix a few thread-safety issue when resetting flags before preloading
```

- 第一条修复了蓝图中使用 Class 类型输出和"全部结果"数组模式时的编译错误，属于重要的 bug 修复
- 第二条是代码质量改进，添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏
- 第三条是底层代码清理和线程安全修复

### 维护评价

- **创建时间**：2022 年 5 月，约 3 年历史，属于较新的插件
- **更新频率**：持续有更新，最近的 commit 涉及 bug 修复和代码质量改进
- **维护状态**：**活跃维护中** — 作为 UE5 动画系统的重要组成部分，Epic 持续投入开发
- **默认启用**：`EnabledByDefault=false`，需要手动在项目设置中启用
- **已知限制**：需要手动启用；学习曲线较陡，需要理解 Chooser Table 和 Proxy Table 的概念
- **推荐程度**：⭐⭐⭐⭐⭐ 强烈推荐用于需要数据驱动资产选择的项目，特别是动画系统复杂的角色

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)
- 官方文档（暂无）