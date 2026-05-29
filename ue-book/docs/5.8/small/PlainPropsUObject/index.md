# PlainPropsUObject

> New Serialization Stack Prototype - CoreUObject Bindings

| 属性 | 值 |
|---|---|
| 中文名 | 新序列化栈原型绑定 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlainPropsUObject` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainPropsUObject) | |

## 用途

PlainPropsUObject 是 Epic 正在开发的**新一代序列化栈原型**，负责将 UE 的 UObject 反射系统（UClass、UScriptStruct、UFunction、UEnum、FProperty）桥接到 PlainProps 序列化框架中。

核心解决的问题：UE 现有的序列化系统基于 FArchive，这套系统已经运行了很多年，存在诸多历史包袱。PlainProps 项目试图构建一个更现代、更高效的序列化栈，而 PlainPropsUObject 是这个新栈与 CoreUObject 反射系统的**绑定层**——它在启动时声明所有原生 UClass/UScriptStruct/UFunction/UEnum，使 PlainProps 能够序列化和反序列化任何 UObject 派生对象。

当前是原型阶段，尚未支持实时编辑（live edit）和延迟加载类型（late-loaded types）等高级功能。

## 使用场景

- **Epic 内部开发**：这是 Epic 用于研究和原型验证的实验性模块，用于探索 UE 序列化系统的现代化方向
- **序列化性能研究**：对比现有 FArchive 序列化与 PlainProps 新栈的性能差异
- **打包 IO 流水线**：为未来的 IOStore/Zen 存储格式提供新的序列化基础
- **数据差异比对**：利用内置的 Diff 功能比较两个 UObject 树之间的差异

> ⚠️ **警告**：此插件为实验性原型，仅支持 Win64，且 `EnabledByDefault=false`。**不建议在生产环境中使用**。

## 蓝图用法

此插件没有任何蓝图可调用的 API。它是一个纯 C++ 运行时模块，仅提供序列化绑定基础设施，不暴露 UFUNCTION 节点。

## C++ 用法

> ⚠️ 此插件需要在 `.uproject` 中添加，并使用命令行参数 `-BindPlainProps` 启用。

### 头文件引入

```cpp
#include "PlainPropsUObjectRuntime.h"
#include "PlainPropsRoundtripTest.h"
```

### 基本用法：Schema 绑定所有类型

启动时将所有原生 UStruct/UEnum 绑定到 PlainProps schema 中：

```cpp
#include "PlainPropsRoundtripTest.h"

using namespace PlainProps::UE;

// 绑定所有类型到 PlainProps 序列化系统
// Mode: All=全部, Source=源码, Runtime=运行时
// BatchType: Plain=普通, Linker=链接器
SchemaBindAllTypes(EBindMode::All, EBatchType::Plain);
```

**来源**: `Source/Public/PlainPropsRoundtripTest.h`

### 基本用法：Roundtrip 测试

通过不同序列化格式往返序列化/反序列化对象，验证数据一致性：

```cpp
#include "PlainPropsRoundtripTest.h"

using namespace PlainProps::UE;

TArray<UObject*> Objects = { MyObject1, MyObject2 };

// 定义往返测试选项
ERoundtrip Options = ERoundtrip::PP | ERoundtrip::TPS | ERoundtrip::UPS | ERoundtrip::TextMemory;

// 通过 PlainBatch 进行往返测试
int32 NumDiffs = RoundtripViaPlainBatch(Objects, Options);

// 通过 LinkerBatch 进行往返测试（带差异过滤器）
FLinkerDiffFilter DiffFilter;
DiffFilter.BypassNativeIdenticalStructs.Add(TEXT("MyStruct"));
DiffFilter.IgnoreStructs.Add(TEXT("IgnoredStruct"));

int32 NumDiffs2 = RoundtripViaLinkerBatch(Objects, Options, DiffFilter, nullptr);
```

**来源**: `Source/Public/PlainPropsRoundtripTest.h`

### 进阶用法：访问全局绑定状态

PlainPropsUObject 维护了一套全局状态 `GUE`，包含所有已注册的类型 ID、名称索引等：

```cpp
#include "PlainPropsUObjectRuntime.h"

using namespace PlainProps::UE;

// 访问全局单例
FGlobals& G = GUE;

// 使用 FRuntimeIds 进行类型索引
FNameId NameId = FRuntimeIds::IndexName("MyStruct");
FMemberId MemberId = FRuntimeIds::IndexMember("Value");
FEnumId EnumId = FRuntimeIds::IndexEnum(G.Scopes.CoreUObject, "EPropertyFlags");

// 绑定默认结构体
G.Defaults.Bind(MyBindId, MyUScriptStruct);
G.Defaults.BindZeroes<MyType>(ZeroBindId);
```

**来源**: `Source/Public/PlainPropsUObjectRuntime.h`

### 进阶用法：自定义类型绑定

为 UE 特定类型（如 FFieldPath、FInstancedStruct）提供自定义序列化绑定：

```cpp
// FInstancedStruct 的自定义绑定示例（由插件内置）
struct FInstancedStructBinding : ICustomBinding
{
    using Type = FInstancedStruct;
    const FMemberId MemberIds[2];

    FInstancedStructBinding(TPropertySpecifier<2>& Spec);
    
    void Save(FMemberBuilder& Dst, const Type& Src, const Type* Default, const FSaveContext&) const;
    void Load(Type& Dst, FStructLoadView Src, ECustomLoadMethod Method) const;
    static bool Diff(const Type& A, const Type& B, const FBindContext&);
};
```

**来源**: `Source/Public/PlainPropsUObjectRuntime.h`

## Demo 示例

```cpp
// MyPlainPropsTest.h
#pragma once

#include "CoreMinimal.h"
#include "PlainPropsRoundtripTest.h"
#include "PlainPropsUObjectRuntime.h"

UCLASS()
class UMyPlainPropsTest : public UObject
{
    GENERATED_BODY()

public:
    // 运行一次完整的序列化往返测试
    static void RunRoundtripTest()
    {
        using namespace PlainProps::UE;

        // 1. 绑定所有原生类型到 PlainProps
        SchemaBindAllTypes(EBindMode::All, EBatchType::Plain);

        // 2. 准备测试对象
        UObject* TestObj = NewObject<UObject>();

        // 3. 执行往返测试，验证 PlainProps 序列化结果与现有系统一致
        ERoundtrip Options = ERoundtrip::PP | ERoundtrip::TextMemory;
        int32 NumDiffs = RoundtripViaPlainBatch({TestObj}, Options);

        if (NumDiffs == 0)
        {
            UE_LOG(LogTemp, Log, TEXT("PlainProps roundtrip test passed!"));
        }
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PlainProps` | 核心序列化框架，提供 FBindId、FSchemaBindings、ICustomBinding 等基础设施 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `95706cb8` | PlainProps: Replace TCustomSpecifier with TPropertySpecifier in MetaBindings. | 统一 MetaBindings 中的 Specifier 命名 |
| 2026-04-14 | `d26343ca` | PlainProps: Tweak FPropertyBinding to write its TEnumAsByte<ELifetimeCondition> BlueprintReplicationCondition | 修复蓝图复制条件的序列化写入 |
| 2026-04-14 | `b6b85039` | PlainProps: Add template constructors for FMemberSpec and TOptionalId to handle implicit conversions | 增加模板构造函数支持隐式类型转换 |
| 2026-04-14 | `efdd698c` | PlainProps: Replace incorrect checkSlow in the debug version of DiffMap with correct handling of different-sized maps | 修复 DiffMap 中不同大小 Map 的调试断言错误 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |

### 维护评价

- **创建时间**：2024-09-19，约 2 年历史
- **活跃状态**：**活跃开发中**——最近一次更新在 2026-04-14，且同一天有 5 次提交，说明正在密集开发
- **开发阶段**：原型阶段，commit message 中明确提到 "initial implementation"、"next step is UStruct and FProperty bindings"
- **限制**：仅支持 Win64，不支持实时编辑和延迟加载类型，需要手动启用
- **推荐**：**仅限 Epic 内部和研究用途**。这是一个低级的序列化基础设施原型，普通开发者无需关注，除非你正在研究 UE 序列化系统的底层改进

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainPropsUObject)
- [PlainProps 父插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainProps)