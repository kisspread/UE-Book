# PlainProps

> New Serialization Stack Prototype

| 属性 | 值 |
|---|---|
| 中文名 | 新序列化原型 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlainProps` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainProps) | |

## 用途

PlainProps 是 Epic 正在开发的**新一代序列化框架原型**，旨在替代 UE 现有的属性系统序列化栈（UProperty/FProperty 体系）。

它解决的核心问题：

1. **编译时类型信息（CTTI）**：通过 `PP_REFLECT_STRUCT` / `PP_REFLECT_ENUM` 等宏在编译期提取结构体成员布局，绕过反射系统运行时开销
2. **高效二进制序列化**：自定义紧凑的 schema + 数据格式，支持 VarInt 编码、位缓存（bit cache）、跳过对齐等优化
3. **增量/Delta 保存**：通过 `FBaseline` 机制只保存与默认值不同的成员，大幅减少序列化体积
4. **版本迁移（Upgrade）**：内置的 schema 版本化升级系统，支持结构体重命名、成员重组、枚举变换等
5. **松散类型系统（Loose Types）**：用于升级过程中的中间表示，允许在 schema 版本间做动态类型转换

**与现有系统的关系**：这不是面向用户的功能插件，而是引擎底层序列化基础设施的原型。它为 Verse 语言（`FVerseString` 绑定可见）和未来 UE 数据管线提供更高效的序列化后端。

## 使用场景

- 你正在开发 UE 底层序列化/数据管线优化 → 研究 PlainProps 的 schema + binding 架构
- 你需要理解 Verse 语言与 UE 的数据交互方式 → PlainProps 提供了 `FVerseString` / `FSensitiveName` 等桥接类型
- 你需要实现自定义类型的高效 delta 序列化 → 参考 `ICustomBinding` 接口和 `FBaseline` 机制
- 你正在研究 UE 的 CTTI（编译时反射）方向 → 学习 `PP_REFLECT_STRUCT` 宏体系

⚠️ **不建议在生产环境使用**。此插件标记为 Experimental 且默认禁用，仅支持 Win64，API 随时可能变化。

## 蓝图用法

此插件**没有暴露任何蓝图 API**。它是纯 C++ 运行时序列化框架，不包含 `UFUNCTION(BlueprintCallable)` 或 `UMG` 相关内容。所有操作都在 C++ 层面完成。

## C++ 用法

### 头文件引入

```cpp
#include "PlainPropsBind.h"        // 绑定系统核心
#include "PlainPropsBindCtti.h"    // CTTI 绑定辅助
#include "PlainPropsCtti.h"        // PP_REFLECT_* 宏
#include "PlainPropsBuild.h"       // 构建中间表示
#include "PlainPropsSave.h"        // 序列化（保存）
#include "PlainPropsLoad.h"        // 反序列化（加载）
#include "PlainPropsLoadMember.h"  // 成员级加载
#include "PlainPropsDeclare.h"     // 结构体/枚举声明
#include "PlainPropsSpecify.h"     // 成员类型指定
```

### 基本用法：声明反射类型

使用 `PP_REFLECT_STRUCT` 宏为原生 C++ 结构体添加编译时反射信息。

```cpp
// 来源: Source/Public/PlainPropsUeCoreBindings.h

// 为 FVector 声明反射，列出所有成员变量
namespace UE::Math
{
PP_REFLECT_STRUCT(, FVector, void, X, Y, Z);
PP_REFLECT_STRUCT(, FVector4, void, X, Y, Z, W);
PP_REFLECT_STRUCT(, FQuat, void, X, Y, Z, W);
PP_REFLECT_STRUCT(, FIntPoint, void, X, Y);
}

// 枚举声明
// PP_REFLECT_ENUM(NS, EnumType, Value1, Value2, ...);
// PP_REFLECT_FLAG_ENUM(NS, FlagType, Flag1, Flag2, ...);  // 每个值必须是单 bit
```

### 基本用法：自定义容器绑定

为 UE 容器类型实现 `IItemRangeBinding` 接口以支持序列化。

```cpp
// 来源: Source/Public/PlainPropsUeCoreBindings.h

template <typename T, class Allocator>
struct TArrayBinding : IItemRangeBinding
{
    using SizeType = int32;
    using ItemType = T;
    using ArrayType = TArray<T, Allocator>;
    
    inline static constexpr std::string_view BindName = TTypename<ArrayType>::RangeBindName;

    // 加载时：分配和构造容器元素
    virtual void MakeItems(FLoadRangeContext& Ctx) const override
    {
        ArrayType& Array = Ctx.Request.GetRange<ArrayType>();
        if constexpr (std::is_default_constructible_v<T>)
        {
            Array.SetNum(Ctx.Request.NumTotal());
        }
        else
        {
            Array.SetNumUninitialized(Ctx.Request.NumTotal());
            Ctx.Items.SetUnconstructed();
        }
        Ctx.Items.Set(Array.GetData(), Ctx.Request.NumTotal());
    }

    // 保存时：读取容器元素
    virtual void ReadItems(FSaveRangeContext& Ctx) const override
    {
        const ArrayType& Array = Ctx.Request.GetRange<ArrayType>();
        Ctx.Items.SetAll(Array.GetData(), static_cast<uint64>(Array.Num()));
    }
};
```

### 进阶用法：自定义结构体绑定（ICustomBinding）

对于引用类型、私有成员、非默认构造类型，实现 `ICustomBinding` 接口。

```cpp
// 来源: Source/Public/PlainPropsBind.h

struct ICustomBinding
{
    virtual ~ICustomBinding() {}
    
    // 保存：将结构体写入 MemberBuilder
    virtual void SaveCustom(FMemberBuilder& Dst, const void* Src, 
                            FBaseline Base, const FSaveContext& Ctx) = 0;
    
    // 加载：从 StructLoadView 读取到结构体
    virtual void LoadCustom(void* Dst, FStructLoadView Src, 
                            ECustomLoadMethod Method) const = 0;
    
    // 差异比较
    virtual bool DiffCustom(const void* StructA, const void* StructB, 
                            const FBindContext& Ctx) const = 0;
    
    // 可选：memcpy 快速加载路径
    virtual void PlanCustom(FMemcpyLoadPlan& Out) const {}
};
```

### 进阶用法：使用 TScopedStructBinding 注册绑定

```cpp
// 来源: Source/Public/PlainPropsBindCtti.h
// TScopedStructBinding 自动管理绑定的注册和注销生命周期

// 对于有 CustomBind<T> 特化的类型
template<class T, class Runtime, typename CustomBinding = CustomBind<T>>
struct TScopedStructBinding : FBothStructId, CustomBinding
{
    // 构造时注册绑定到 Runtime::GetCustoms()
    // 析构时自动注销
    ~TScopedStructBinding() { Runtime::GetCustoms().DropStruct(BindId); }
};

// 对于 Schema-bound 结构体（无自定义绑定）
template<class T, class Runtime>
struct TScopedStructBinding<T, Runtime, void> : FBothStructId
{
    // 构造时调用 BindNativeStruct
    ~TScopedStructBinding() { Runtime::GetSchemas().DropStruct(BindId); }
};
```

### 进阶用法：保存和加载

```cpp
// 来源: Source/Public/PlainPropsSave.h

// 保存整个结构体
FBuiltStruct* Saved = SaveStruct(MyStructPtr, BindId, SaveContext);

// 保存增量（仅与默认值不同的部分）
FBuiltStruct* Delta = SaveStructDelta(MyStructPtr, Baseline, BindId, SaveContext);

// 仅在有差异时保存
FBuiltStruct* Diff = SaveStructDeltaIfDiff(MyStructPtr, Baseline, BindId, SaveContext);

// 来源: Source/Public/PlainPropsLoadMember.h

// 加载结构体
LoadStruct(DstPtr, SrcView);

// 快速加载单个叶子成员
int32 Value = LoadSole<int32>(SrcView);
```

## Demo 示例

最小示例：声明一个结构体并使用 MemberBuilder 构建序列化数据。

```cpp
// MyData.h
#pragma once
#include "PlainPropsCtti.h"
#include "PlainPropsBuild.h"
#include "PlainPropsSpecify.h"
#include "PlainPropsDeclare.h"

namespace MyGame
{

struct FPosition
{
    float X;
    float Y;
    float Z;
};

// 使用 PP_REFLECT_STRUCT 宏声明反射
PP_REFLECT_STRUCT(MyGame, FPosition, void, X, Y, Z)

} // namespace MyGame
```

```cpp
// MySerialization.cpp
#include "MyData.h"
#include "PlainPropsBuild.h"
#include "PlainPropsIndex.h"
#include "PlainPropsBindCtti.h"

using namespace PlainProps;

// 创建 ID 索引器（使用 FName）
static TIdIndexer<FName> GIds;

// 声明结构体 schema
static FDeclId PositionDeclId = GIds.IndexDeclId(FType{
    GIds.MakeScope("MyGame"), 
    GIds.MakeTypename("FPosition")
});

static FMemberId XId = GIds.NameMember("X");
static FMemberId YId = GIds.NameMember("Y");
static FMemberId ZId = GIds.NameMember("Z");

// 构建序列化数据
void SavePosition(const MyGame::FPosition& Pos)
{
    FScratchAllocator Scratch;
    FMemberBuilder Builder;
    
    // 添加叶子成员
    Builder.Add(XId, Pos.X);  // float 自动处理
    Builder.Add(YId, Pos.Y);
    Builder.Add(ZId, Pos.Z);
    
    // 构建为 FBuiltStruct（需要预先声明结构体 schema）
    // 实际使用中需要完整的 FStructDeclaration 和 IDeclarations
    // FBuiltStruct* Built = Builder.BuildAndReset(Scratch, Declaration, DebugIds);
}
```

## 模块依赖

从源码分析，PlainProps 模块的 Build.cs 未在提供的信息中展示，但根据头文件引用推断：

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine 等） | 该插件主要依赖 UE 基础类型（FName, TArray, TSet 等），不依赖编辑器或其他插件模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的输出错误 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数大小不匹配的问题 |
| 2026-04-14 | `b6b85039` | PlainProps: Add template constructors for FMemberSpec and TOptionalId to handle implicit conversions | 为 FMemberSpec 和 TOptionalId 添加模板构造函数以处理隐式转换 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到 UE_LOGF |
| 2026-04-09 | `cea78a89` | PlainProps: TExternallyBound struct trait to skip BindCustomStructOnce singleton for externally bound | 添加 TExternallyBound trait 以跳过外部绑定的单例注册 |

### 维护评价

- **活跃维护**：最近一个月内有多次实质性提交，说明仍在积极开发
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，仅支持 Win64
- **创建时间**：2024 年 5 月，约 2 年历史，属于较新的实验性框架
- **Commit 内容**：近期更新以 bug 修复和 API 完善为主（格式化修复、隐式转换支持、外部绑定支持），表明该框架正在趋于稳定
- **代码成熟度**：58 个源文件，架构完整（CTTI → Build → Save/Load → Diff → Upgrade），但仍有大量注释代码和 TODO 标记
- **⚠️ 警告**：这是引擎底层序列化原型，API 随 UE 版本迭代可能大幅变化。不建议外部项目依赖，仅适合研究 UE 未来序列化架构方向时参考

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PlainProps)
- 官方文档（无）