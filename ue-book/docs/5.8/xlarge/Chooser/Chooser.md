# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 中文名 | 选择器表 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类型、动画节点） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Runtime), `ChooserUncooked` (Runtime), `ProxyTable` (Runtime), `ProxyTableEditor` (Runtime), `ProxyTableUncooked` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser) | |

## 用途

Chooser 是一个**动态资产选择系统**，本质上是一个带有条件过滤逻辑的"决策表"。它解决的核心问题是：**根据运行时的上下文参数，从一组候选项中自动选择最匹配的结果**。

与普通 Data Table 的关键区别：
- **每列是一个过滤条件**：列可以读取上下文对象的属性（如枚举值、布尔值、GameplayTag、浮点范围等），用于过滤行
- **支持多列组合过滤**：多个条件必须同时满足，类似 SQL 的 WHERE 子句
- **支持加权随机选择**：通过 Randomize 列实现概率分布选择
- **支持成本评分**：通过 FloatDistance 等列对候选项进行评分排序
- **支持嵌套 Chooser**：结果可以是另一个 Chooser 的评估结果，实现递归决策
- **结果类型多样**：可返回 UObject 引用、UClass 类型、或仅写入输出参数

典型应用场景：一个角色有多种动画需要根据状态组合选择，传统方式需要大量 if-else 或 switch-case，用 Chooser 可以将这些决策逻辑做成可视化的表格资产，策划可以直接编辑而无需改代码。

## 使用场景

- 你需要根据角色状态（移动/攻击/受伤）+ 环境（室内/室外/水中）动态选择动画蒙太奇 → 用 ChooserTable + 多个枚举/布尔列
- 你需要根据玩家等级、职业、地区等因素选择不同的奖励池 → 用 ChooserTable + 枚举列 + 随机列
- 你需要一个可由策划维护的决策表来选择 AI 行为树或角色蓝图 → 用 ChooserTable + Object 列返回 Class 或 Asset
- 你需要根据浮点值（如距离、速度、角度）选择最匹配的动画 → 用 FloatDistance 列进行成本评分
- 你需要在动画蓝图中根据条件动态切换动画 → 用 AnimNode_ChooserPlayer

## 蓝图用法

Chooser 的蓝图 API 主要通过 `UChooserFunctionLibrary` 暴露，大多数节点标记为 `BlueprintInternalUseOnly`，意味着它们通常被 Chooser 编辑器自动生成的蓝图逻辑使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateChooser` | 评估 Chooser 表，返回第一个匹配的 UObject（或 null） | `UChooserFunctionLibrary` |
| `EvaluateChooserMulti` | 评估 Chooser 表，返回所有匹配的 UObject 列表 | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBase` | 通用评估接口，支持 Chooser 表和代理表 | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBaseMulti` | 通用多结果评估接口 | `UChooserFunctionLibrary` |
| `EvaluateObjectChooserBaseSoft` | 返回软引用的评估接口 | `UChooserFunctionLibrary` |
| `AddChooserObjectInput` | 向评估上下文添加一个 UObject 参数 | `UChooserFunctionLibrary` |
| `GetChooserObjectInput` | 从评估上下文按索引获取一个 UObject 参数 | `UChooserFunctionLibrary` |
| `GetChooserObject` | 从评估上下文按类/接口类型获取对象（实验性） | `UChooserFunctionLibrary` |
| `AddChooserStructInput` | 向评估上下文添加一个 Struct 参数 | `UChooserFunctionLibrary` |
| `AddChooserStructInputOutput` | 向评估上下文添加一个可读写的 Struct 参数 | `UChooserFunctionLibrary` |
| `GetChooserStructOutput` | 从评估上下文获取输出 Struct 值 | `UChooserFunctionLibrary` |
| `MakeEvaluateChooser` | 创建一个 FEvaluateChooser 实例，引用指定 Chooser 表 | `UChooserFunctionLibrary` |
| `MakeChooserEvaluationContext` | 创建一个空的评估上下文 | `UChooserFunctionLibrary` |

### 使用示例（蓝图描述）

**基本评估流程**：

1. 创建 `FChooserEvaluationContext`：调用 `MakeChooserEvaluationContext` 创建上下文对象
2. 添加输入参数：调用 `AddChooserObjectInput` 传入当前角色 Actor；调用 `AddChooserStructInput` 传入自定义状态结构体
3. 评估 Chooser：调用 `EvaluateObjectChooserBase`，传入上下文、ChoosrTable 资产引用、期望的结果类型
4. 使用结果：返回的 UObject 就是最匹配的行的结果（动画蒙太奇、角色蓝图等）

**动画蓝图中使用**：

在动画蓝图中添加 `Chooser Player` 节点（AnimNode_ChooserPlayer），在 Details 面板中：
- 设置 `Chooser` 属性为 `Evaluate Chooser` 类型，并选择对应的 ChooserTable 资产
- 配置 `EvaluationFrequency`（OnBecomeRelevant / OnUpdate / OnLoop 等）
- 设置 BlendSpace 参数、镜像表、默认播放设置等

## C++ 用法

### 头文件引入

```cpp
#include "Chooser.h"
#include "ChooserFunctionLibrary.h"
#include "IObjectChooser.h"
```

### 基本用法

从 UChooserTable 的核心评估 API 提取：

```cpp
#include "Chooser.h"
#include "IObjectChooser.h"

// 基本的 Chooser 评估（来源：Public/Chooser.h）
// 创建评估上下文并评估 Chooser 表
FChooserEvaluationContext Context;
Context.AddObjectParam(MyCharacter);  // 添加上下文对象

// 评估 Chooser，通过回调收集结果
const UChooserTable* MyChooserTable = /* 加载你的 ChooserTable 资产 */;
UChooserTable::EvaluateChooser(Context, MyChooserTable,
    FObjectChooserBase::FObjectChooserIteratorCallback::CreateLambda(
        [](UObject* Result) -> FObjectChooserBase::EIteratorStatus
        {
            if (Result)
            {
                // 使用结果，例如播放动画蒙太奇
                UE_LOG(LogTemp, Log, TEXT("Selected: %s"), *Result->GetName());
                return FObjectChooserBase::EIteratorStatus::Stop;  // 只取第一个结果
            }
            return FObjectChooserBase::EIteratorStatus::Continue;
        }
    ));
```

### 进阶用法

使用函数库进行评估，并处理输出参数：

```cpp
#include "Chooser.h"
#include "ChooserFunctionLibrary.h"
#include "IObjectChooser.h"

// 来源：Public/ChooserFunctionLibrary.h + Public/IObjectChooser.h
void EvaluateChooserWithOutputs(UObject* ContextObject, UChooserTable* ChooserTable)
{
    // 方法1：简单的单结果评估（需要 ObjectClass 模板参数）
    UObject* Result = UChooserFunctionLibrary::EvaluateChooser(
        ContextObject, ChooserTable, UObject::StaticClass());
    
    if (Result)
    {
        // 处理结果
    }

    // 方法2：带自定义上下文的通用评估
    FChooserEvaluationContext Context;
    Context.AddObjectParam(ContextObject);
    
    // 添加自定义 Struct 参数（输入）
    FChooserPlayerSettings Settings;
    Context.AddStructParam(Settings);
    
    // 使用 FInstancedStruct 包装的 ObjectChooser
    FInstancedStruct ObjectChooser;
    ObjectChooser.InitializeAs<FEvaluateChooser>();
    FEvaluateChooser& EvalChooser = ObjectChooser.GetMutable<FEvaluateChooser>();
    EvalChooser.Chooser = ChooserTable;
    
    // 评估并获取结果
    UObject* EvalResult = UChooserFunctionLibrary::EvaluateObjectChooserBase(
        Context, ObjectChooser, UObject::StaticClass(), false);

    // 方法3：多结果评估
    TArray<UObject*> AllResults = UChooserFunctionLibrary::EvaluateChooserMulti(
        ContextObject, ChooserTable, UObject::StaticClass());
}
```

## 模块依赖

从 Build.cs 和源码推断的独特依赖（省略常见的 Core/CoreUObject/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | GameplayTag 列的过滤逻辑和标签容器操作 |
| `PropertyPath` | 属性绑定链的解析和编译 |
| `StructUtils` | FInstancedStruct 和 FStructView 的使用 |
| `AnimGraphRuntime` | AnimNode_ChooserPlayer 动画图节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `aad6fe75` | Remove build setting making chooser internal headers public, and move most of those internal headers | 清理内部头文件的可见性，将内部头文件移至 Private 目录 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `333cccbc` | Add profiling tag to chooser property access | 为 Chooser 属性访问添加性能分析标签 |
| 2026-04-17 | `1eda8a87` | Fix chooser editor null pointer crash after native context type rename | 修复原生上下文类型重命名后编辑器空指针崩溃 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器新增数据资产创建菜单集成 |

### 维护评价

**🟢 活跃维护**

- **创建时间**：2024 年 9 月，从 Experimental 文件夹迁移而来（commit 原文：`Move Chooser plugin out of Experimental folder`）
- **更新频率**：最近 1 个月内有多次实质性更新，包括代码清理、bug 修复、性能优化
- **维护状态**：处于积极维护阶段，有持续的功能完善和问题修复
- **已知注意事项**：
  - 需要手动启用（`EnabledByDefault: false`），需在 Project Settings → Plugins 中开启
  - 依赖 `GameplayTagsEditor` 插件
  - 部分功能标记为实验性（如 `GetChooserObject` 函数、`ForceBlendTo` 设置等）
- **推荐使用**：✅ 推荐。这是一个成熟的 Epic 官方插件，已从实验阶段毕业，文档结构完善，适合需要复杂动态资产选择逻辑的项目使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Chooser)
- [官方文档]()（暂无）