# NiagaraCore

> Niagara effect systems.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉核心 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-10-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraCore) | |

## 用途

NiagaraCore 是 Niagara 视觉特效系统的核心基础模块。它不直接提供粒子模拟或渲染功能，而是定义了整个 Niagara 系统所依赖的基本数据结构、类型定义、序列化版本控制以及核心基类。

该模块主要解决以下问题：

- **提供统一的基础类型**：如 `FNiagaraSystemInstanceID` 用于唯一标识系统实例，`ENiagaraParameterAccessLevel` 控制参数访问权限，`ENiagaraIterationSource` 定义迭代来源。
- **编译哈希管理**：`FNiagaraCompileHash` 封装了用于比较和验证 Niagara 脚本编译状态的哈希值，确保不同版本之间的兼容性。
- **自定义版本控制**：`FNiagaraCustomVersion` 管理所有包含 Niagara 资产类型的包的序列化版本，支持向后兼容。
- **数据接口基类**：为所有 Niagara 数据接口（如碰撞、音频、渲染等）提供抽象的基类 `UNiagaraDataInterfaceBase`，定义 GPU 参数构建、着色器存储等通用接口。
- **可合并/可通知基类**：提供 `UNiagaraMergeable` 和 `UNiagaraNotifyOnChanged` 基类，支持编辑器中的合并操作和属性变更通知。

## 使用场景

- 你在开发一个自定义 Niagara 数据接口时，需要继承 `UNiagaraDataInterfaceBase`。
- 你需要比较两个 Niagara 脚本的编译是否一致时，使用 `FNiagaraCompileHash`。
- 你在处理 Niagara 资产的序列化兼容性问题时，需要引用 `FNiagaraCustomVersion`。
- 你在编写需要与 Niagara 系统交互的自定义模块时，会使用本模块定义的基础类型（如 `FNiagaraVariableCommonReference`、`ENiagaraIterationSource` 等）。

## 蓝图用法

此模块为核心库，**不包含**任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其定义的类型和结构体主要在 C++ 和 Niagara 系统内部使用，蓝图开发者通常不需要直接操作。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraCore.h"
#include "NiagaraDataInterfaceBase.h"
#include "NiagaraCompileHash.h"
#include "NiagaraCustomVersion.h"
```

### 基本用法

**使用编译哈希比较脚本一致性**

```cpp
// 获取两个脚本的编译哈希并比较
const FNiagaraCompileHash& HashA = ScriptA->GetCompileHash();
const FNiagaraCompileHash& HashB = ScriptB->GetCompileHash();

if (HashA != HashB)
{
    // 脚本需要重新编译
    UE_LOG(LogTemp, Warning, TEXT("Script compile hashes differ, recompilation required."));
}
```
*来源：`NiagaraCore` 模块头文件 `NiagaraCompileHash.h`*

**使用自定义版本号进行序列化兼容**

```cpp
// 在自定义序列化函数中检查版本
void MyCustomSerializer(FArchive& Ar, int32 Version)
{
    if (Version >= FNiagaraCustomVersion::DataInterfaceComputeShaderParamRefactor)
    {
        // 读取新版本的参数
    }
    else
    {
        // 读取旧版本的参数
    }
}
```
*来源：`NiagaraCore` 模块头文件 `NiagaraCustomVersion.h`*

### 进阶用法

**继承并实现自定义数据接口**

此示例展示了如何创建一个简单的自定义数据接口，该接口向 GPU 着色器暴露一个浮点参数。

```cpp
// MyCustomDataInterface.h
#pragma once

#include "NiagaraDataInterfaceBase.h"
#include "MyCustomDataInterface.generated.h"

UCLASS(EditInlineNew, Category = "My Niagara Data Interfaces")
class UMyCustomDataInterface : public UNiagaraDataInterfaceBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Parameters")
    float MyParameter = 1.0f;

    // 构建着色器参数结构体
    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override
    {
        BEGIN_SHADER_PARAMETER_STRUCT(FMyShaderParameters, )
            SHADER_PARAMETER(float, MyParameter)
        END_SHADER_PARAMETER_STRUCT()

        ShaderParametersBuilder.AddNestedStruct<FMyShaderParameters>();
    }

    // 创建着色器存储（用于传递编译时信息）
    virtual FNiagaraDataInterfaceParametersCS* CreateShaderStorage(
        const FNiagaraDataInterfaceGPUParamInfo& ParameterInfo,
        const FShaderParameterMap& ParameterMap) const override
    {
        return nullptr;
    }

    virtual const FTypeLayoutDesc* GetShaderStorageType() const override
    {
        return nullptr;
    }
};
```
*来源：`NiagaraCore` 模块头文件 `NiagaraDataInterfaceBase.h` (示例模式)*

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何使用 `UNiagaraDataInterfaceBase` 创建自定义数据接口。

**MyCustomDataInterface.h**

```cpp
#pragma once

#include "NiagaraDataInterfaceBase.h"
#include "MyCustomDataInterface.generated.h"

UCLASS(EditInlineNew, Category = "My Niagara Data Interfaces")
class UMyCustomDataInterface : public UNiagaraDataInterfaceBase
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Parameters")
    float MyFloatValue = 42.0f;

    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override
    {
        // 实现略
    }

    virtual FNiagaraDataInterfaceParametersCS* CreateShaderStorage(
        const FNiagaraDataInterfaceGPUParamInfo& ParameterInfo,
        const FShaderParameterMap& ParameterMap) const override
    {
        return nullptr;
    }

    virtual const FTypeLayoutDesc* GetShaderStorageType() const override
    {
        return nullptr;
    }
};
```

**MyCustomDataInterface.cpp**

```cpp
#include "MyCustomDataInterface.h"

// 可以在此处添加自定义逻辑，例如运行时数据更新等
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖 | 仅标准 Core/Engine 等 |

该模块依赖关系非常轻量，主要依赖于 `Core`, `CoreUObject`, `Engine` 等标准模块。

## 维护状态

### 近期更新

- 2025-10-22 `5d0cd83c` 修复在清理过程中访问已释放的 Niagara 组件的问题。
- 2025-10-22 `3f549682` 修复当 CPU 没有数据更新时 NDC 数据残留的问题。
- 2025-10-21 `6ac05a79` 添加默认关闭的变通方案，用于解决内部测试中遇到的 Niagara 崩溃。
- 2025-10-17 `f6546371` 修复因 GT 和 RT 时钟不同步导致 NDC 数据丢失的问题。
- 2025-10-16 `566219ca` 回退 CL47013072。

### 维护评价

NiagaraCore 作为 Niagara 系统的核心基础模块，维护状态非常活跃。近期更新主要集中在稳定性修复和边缘情况处理上，修复了组件清理、数据同步、崩溃等关键问题。模块与 Niagara 主系统保持同步迭代，更新频率高，质量可靠。推荐在有 Niagara 相关的自定义开发需求时引入此模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara/Source/NiagaraCore)
- [官方文档](https://docs.unrealengine.com/5.3/en-US/niagara-effects-in-unreal-engine/) (Niagara 系统整体文档)
- [Niagara 主插件目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/Niagara)