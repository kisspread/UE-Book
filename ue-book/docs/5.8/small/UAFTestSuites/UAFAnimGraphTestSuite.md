# UAF Tests

> UAF Automated Tests

| 属性 | 值 |
|---|---|
| 中文名 | UAF 自动化测试 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、测试数据） |
| 模块 | `UAFCQTestSuite` (Editor), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimNodeTestData` (Runtime), `UAFTestSuite` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites) | |

## 用途

这是一个专为 **UAF (Unreal Animation Framework)** 设计的自动化测试套件。它不包含任何实际的生产功能，而是用于验证 UAF 核心组件（如动画图、特性（Trait）系统、动画节点、序列化等）的正确性、稳定性和边界情况。插件的名称从 `UAFTests` 更改为 `UAFTestSuites`，表明其作为测试集合的定位。

## 使用场景

这个插件**不面向最终用户或游戏开发者**，而是服务于 Unreal Engine 的核心开发人员。主要使用场景是：
- **UAF 系统开发与维护**：在开发 UAF 新功能或修复 Bug 时，运行此插件中的测试用例来确保改动没有引入回归问题。
- **持续集成 (CI)**：作为自动化构建流水线的一部分，用于在每次代码提交后自动验证 UAF 模块的健康状态。
- **功能验证**：验证动画特性（Trait）的序列化、事件传播、图实例化、GC（垃圾回收）等复杂机制是否按预期工作。

## 蓝图用法

**此插件不提供任何可直接在游戏或编辑器蓝图中使用的节点。** 它的所有内容都是为了运行自动化测试而构建的，这些测试通过 Unreal Engine 的 **Automation 测试框架** (F自动化测试) 来执行和报告结果。

## C++ 用法

该插件的 C++ 代码主要是测试用例和测试辅助工具，不作为公共 API 使用。以下信息展示了其内部结构，用于理解测试是如何组织的。

### 测试用例结构示例

测试用例通常基于特定的 `FAnimNextTraitSharedData` 派生结构来构建测试数据。

```cpp
// 文件: Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimGraphTestSuite/Private/AnimNextTraitBaseTest.h

// 用于测试基本特性（Trait）共享数据的结构
USTRUCT()
struct FTraitA_BaseSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY(meta = (Inline))
	uint32 TraitUID; // 特性唯一标识符

	FTraitA_BaseSharedData();
};

// 用于测试特性序列化的复杂结构
USTRUCT()
struct FTraitSerialization_BaseSharedData : public FAnimNextTraitSharedData
{
	GENERATED_BODY()

	UPROPERTY(meta = (Inline))
	int32 Integer = 0;
	
	UPROPERTY(meta = (Inline))
	FVector Vector = FVector::ZeroVector;
	
	UPROPERTY(meta = (Inline))
	TArray<FVector> VectorTArray; // 动态数组测试
	
	UPROPERTY(meta = (Inline))
	FString String;
	// ... 更多属性
};
```

### 测试工具函数

插件提供了一些辅助函数来简化测试逻辑。

```cpp
// 文件: Engine/Plugins/Experimental/UAF/UAFTestSuites/Source/UAFAnimGraphTestSuite/Private/AnimNextRuntimeTest.h

namespace UE::UAF
{
	// 将属性值转换为其字符串表示形式，用于测试输出
	template<class TraitSharedDataType, typename PropertyType>
	static FString ToString(const FString& PropertyName, PropertyType PropertyValue)
	{
		// ... 使用 UE 反射进行转换
	}

	// 作用域管理工具，用于临时清理和恢复节点模板注册表状态
	struct FScopedClearNodeTemplateRegistry final
	{
		UAFANIMGRAPHTESTSUITE_API FScopedClearNodeTemplateRegistry();
		UAFANIMGRAPHTESTSUITE_API ~FScopedClearNodeTemplateRegistry();
		// ...
	};

	struct FTestUtils final
	{
		// 从存档缓冲区加载模块数据并解析节点句柄
		static UAFANIMGRAPHTESTSUITE_API bool LoadFromArchiveBuffer(UUAFAnimGraph& AnimationGraph, TArray<FNodeHandle>& NodeHandles, const TArray<uint8>& SharedDataArchiveBuffer);
	};
}
```

## Demo 示例

由于这是测试套件，没有独立的可运行 Demo。要体验其功能，您需要：
1. 确保此插件已启用。
2. 在 Unreal Editor 中，打开 **测试 (Automation)** 窗口。
3. 筛选或搜索包含 “UAF”、“AnimNext”、“Trait” 等关键词的测试用例。
4. 选择并运行这些测试。结果将直接在测试窗口中显示。

## 模块依赖

该插件的模块主要依赖于 UAF 的核心模块，用于构建测试环境和访问被测试的 API。

| 模块 | 用途 |
|---|---|
| `AnimNext` | UAF 的核心运行时模块，被测试的主要对象 |
| `RigVM` | 提供 RigVM（可视化脚本运行时）支持，用于测试动画图执行 |
| `PropertyEditor` | 用于测试与编辑器属性面板相关的功能 |
| `Slate`, `SlateCore` | 构建测试相关的 UI（如有） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复编译器类型转换警告的可移植性问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配的问题。 |
| 2026-04-14 | `12eb7efc` | Fix FBindableXxx binding serialization issues when used with UAF traits | 修复 UAF 特性中绑定序列化的错误。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移到新的 UE_LOGF。 |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 将函数重命名为 GetOrAddComponent 以更准确地反映其行为。 |

### 维护评价

这是一个**活跃维护**的测试插件。
- **年龄**：创建于 2026 年 2 月，非常年轻，与 UE5 最新的 UAF 开发同步。
- **更新频率**：最近几个月有多次提交，内容聚焦于修复编译警告、序列化 Bug 和重构，表明它随着 UAF 核心代码一起被积极维护。
- **状态**：作为 UAF 系统的**实验性**测试套件，它伴随着 UAF 核心模块的发展而持续更新。没有废弃迹象。
- **推荐**：仅推荐给 **Unreal Engine 核心开发人员**或深入研究 UAF 框架内部机制的开发者。普通游戏项目无需关注此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFTestSuites)
- [官方文档]() (无)