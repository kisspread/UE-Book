# PlainPropsUObject

> New Serialization Stack Prototype - CoreUObject Bindings

| 属性 | 值 |
|---|---|
| 中文名 | 核心对象绑定层 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlainPropsUObject` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainPropsUObject) | |

## 用途

PlainPropsUObject 是 Unreal Engine 实验性序列化栈 **PlainProps** 的 CoreUObject 绑定层。PlainProps 旨在提供一种新的、高效的序列化方案，支持紧凑的内存布局和快速的读写。该插件将 PlainProps 的能力与 UObject 体系集成，使 UObject、UStruct、UEnum 等 CoreUObject 类型能够通过 PlainProps 进行序列化/反序列化。

**为什么存在？**
- 默认的 FArchive 序列化路径（如 FObjectWriter/FObjectReader）存在性能瓶颈，PlainProps 尝试绕过标准 UE 序列化流程，直接利用属性元数据进行二进制打包。
- 该插件是 PlainProps 框架与 UObject 世界的桥梁，让现有游戏代码可以逐步迁移至新的序列化堆栈。

## 使用场景

- 需要更高性能的 UObject 序列化（如网络复制、存档、快照）
- 探索下一代 UE 序列化方案，参与原型验证
- 配合 PlainProps 核心库，对复杂 UObject 结构进行批量 roundtrip 测试

## 蓝图用法

该插件**未暴露任何 BlueprintCallable 或 BlueprintReadWrite 接口**。所有功能均为 C++ 原生层操作，仅用于模块初始化与测试。

## C++ 用法

### 头文件引入

```cpp
#include "PlainPropsUObjectRuntime.h"
#include "PlainPropsRoundtripTest.h"
```

### 基本用法

1. **初始化绑定**  
   在游戏启动时（例如模块 StartupModule 中），调用 `SchemaBindAllTypes` 注册所有 UObject 类型的 PlainProps 模式。

   ```cpp
   // 绑定所有类型（Source 模式会注册每个 UObject 类型的属性）
   PlainProps::UE::SchemaBindAllTypes(PlainProps::UE::EBindMode::All);
   ```

2. **执行 Roundtrip 测试**  
   对一组 UObject 进行序列化/反序列化 roundtrip，验证数据一致性。

   ```cpp
   TArray<UObject*> Objects = GetSomeObjects();
   
   // 通过批量序列化进行 roundtrip
   int32 NumErrors = PlainProps::UE::RoundtripViaBatch(Objects, PlainProps::UE::ERoundtrip::PP);
   
   // 或者通过临时包进行 roundtrip（模拟保存/加载）
   int32 NumErrors2 = PlainProps::UE::RoundtripViaPackages(Objects, PlainProps::UE::ERoundtrip::PP | PlainProps::UE::ERoundtrip::TextMemory);
   ```

### 进阶用法

**自定义默认结构体实例**  
如果某个结构体需要非零默认值，可使用 `FDefaultStructs` 进行注册。

```cpp
PlainProps::UE::FDefaultStructs Defaults;
const UScriptStruct* MyStruct = ...; // 例如 FVector::StaticStruct()

// 绑定零值默认实例（大小和对齐）
Defaults.BindZeroes(SomeBindId, sizeof(FVector), alignof(FVector));

// 绑定特定的静态实例（例如某个预设值）
FVector StaticValue(1.0f, 2.0f, 3.0f);
Defaults.BindStatic(SomeBindId, &StaticValue);

// 获取实例
const void* Instance = Defaults.Get(SomeBindId);
```

## Demo 示例

以下是一个最小模块示例，展示如何在项目中使用 PlainPropsUObject 进行 roundtrip 测试。

```cpp
// MyModule.h
#pragma once
#include "Modules/ModuleInterface.h"
#include "PlainPropsRoundtripTest.h"

class FMyModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyModule.cpp
#include "MyModule.h"
#include "PlainPropsUObjectRuntime.h"

IMPLEMENT_MODULE(FMyModule, MyModule);

void FMyModule::StartupModule()
{
    // 注册所有 UObject 类型
    PlainProps::UE::SchemaBindAllTypes(PlainProps::UE::EBindMode::All);
    
    // 示例：对一个 UObject 进行 roundtrip 测试
    // （实际场景中 Objects 应从外部获取）
    TArray<UObject*> Objects;
    if (UObject* Obj = NewObject<UObject>())
    {
        Objects.Add(Obj);
    }
    
    int32 Errors = PlainProps::UE::RoundtripViaBatch(Objects, PlainProps::UE::ERoundtrip::PP);
    UE_LOG(LogTemp, Log, TEXT("Roundtrip errors: %d"), Errors);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PlainProps` | 核心 PlainProps 序列化堆栈（类型系统、二进制编码） |

> 说明：`PlainProps` 同为实验性插件，需手动启用。其他依赖（CoreUObject, Core 等）为 UE 标准模块，不单独列出。

## 维护状态

### 近期更新

- 2025-09-23 `6a308008` — [Core] Fix crash caused when copying empty compact set with inline allocators（与此插件间接相关，修复容器）
- 2025-09-12 `5f19e03c` — [Backout] - CL45790694（回退一个提交）
- 2025-09-12 `820dcbc0` — [Backout] - CL45785126（回退一个提交）
- 2025-09-12 `c40b5a4d` — [Core] Add support to compile switch between using sparse or compact sets as the default set container（Core 底层更改）
- 2025-09-02 `39af566d` — PlainProps preparing to add custom bindings for Engine types（本插件的早期提交，准备引擎类型绑定）

### 维护评价

- **创建时间**：2025-09-02（约 2 个月）
- **最近更新**：2025-09-23 有核心修复提交，表明项目仍在活动。
- **活跃度**：插件处于早期实验阶段，会有频繁的底层调整和回退，但持续有维护提交。
- **推荐使用**：仅推荐用于**原型验证**或**性能测试**，不建议在生产项目中使用。由于 `IsExperimentalVersion=true` 且默认未启用，API 可能在后续版本中发生不兼容变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainPropsUObject)
- [PlainProps 主仓库（推测）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PlainProps)（未在 .uplugin 中直接指定）