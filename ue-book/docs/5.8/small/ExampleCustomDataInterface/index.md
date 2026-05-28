# Niagara Example Custom DataInterface

> This plugin contains C++ example content that shows how to write your own data interface for Niagara.

| 属性 | 值 |
|---|---|
| 中文名 | 数据接口示例 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 源码示例） |
| 模块 | `ExampleCustomDataInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-11-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/ExampleCustomDataInterface) | |

## 用途

这是一个**教学性质**的插件，其核心价值在于展示如何从头开始创建一个自定义的 Niagara 数据接口（Data Interface）。它解决的问题是为 Niagara 粒子系统提供自定义数据源。

插件本身不提供实际的游戏内功能（如特定的粒子效果），而是作为一个完整的、可运行的参考范例。开发者可以通过研究其源码，学习如何将外部数据（如鼠标位置、游戏逻辑中的数据、外部设备数据等）安全且高效地注入到 Niagara 的 CPU 和 GPU 计算管线中。

## 使用场景

*   **学习自定义数据接口**：当你需要为 Niagara 粒子系统创建一个全新的、引擎未提供的数据输入类型时，此插件是绝佳的学习材料。
*   **理解数据接口生命周期**：了解一个数据接口如何管理其**每实例数据（Per-Instance Data）**，如何在 CPU 和 GPU 之间同步数据，以及如何与 Niagara 系统实例交互。
*   **参考代码架构**：当你准备开发自己的、用于生产环境的自定义数据接口时，可以参考此插件中声明类、绑定虚拟机（VM）函数、生成 HLSL 代码以及设置着色器参数的标准模式。

## 蓝图用法

此插件作为底层的 C++ 数据接口实现，本身不直接暴露供蓝图使用的函数节点。其功能将通过 Niagara 系统和发射器（Emitter）间接使用：

1.  在 Niagara 发射器的“粒子生成”或“粒子更新”模块中，你可以添加一个“数据接口”模块。
2.  在该模块的设置中，选择数据接口类型。如果此插件已正确启用和编译，你会在列表中看到 **“MousePosition Query”**（由 `UCLASS` 的 `meta = (DisplayName = “MousePosition Query”)` 定义）。
3.  选择该数据接口后，就可以在 Niagara 脚本中调用其提供的函数（例如 `Get Mouse Position`）来获取数据，驱动粒子行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetMousePosition` | 在 Niagara 脚本中调用，用于获取当前帧的鼠标位置数据 | `UNiagaraDataInterfaceMousePosition` |

### 使用示例（蓝图描述）

1.  创建一个 Niagara 系统。
2.  在发射器更新模块中，添加一个“Particle Attribute”模块。
3.  将该模块的“Data Interface”属性设置为“MousePosition Query”。
4.  在模块脚本中，使用“Get Mouse Position”节点。
5.  将该节点输出的“Mouse Position”（Vector）连接到你想要影响的粒子属性（如“Sprite Position”或“Sprite Size”）上。这样，粒子就会跟随鼠标位置移动或变化。

## C++ 用法

此插件的核心代码集中在 `UNiagaraDataInterfaceMousePosition` 类中，展示了实现一个数据接口所需的关键步骤。

### 头文件引入

```cpp
#include "NiagaraDataInterface.h"
```

### 基本用法：声明与继承

你需要创建一个继承自 `UNiagaraDataInterface` 的类。

```cpp
// 来自: Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h
UCLASS(EditInlineNew, Category = “Mouse”, meta = (DisplayName = “MousePosition Query”))
class UNiagaraDataInterfaceMousePosition : public UNiagaraDataInterface
{
    GENERATED_UCLASS_BODY()
    // ... 类成员和虚函数声明 ...
};
```

### 核心函数实现

一个自定义数据接口必须重写几个关键虚函数：

1.  **提供外部函数**：`GetVMExternalFunction` 将你的 C++ 函数绑定到 Niagara 脚本虚拟机。
2.  **管理每实例数据**：`InitPerInstanceData`, `PerInstanceTick`, `DestroyPerInstanceData`, `PerInstanceDataSize` 用于管理每个 Niagara 系统实例独有的数据。
3.  **GPU 支持（可选但重要）**：`GetFunctionsInternal` (在编辑器中提供函数签名), `GetFunctionHLSL` (为每个函数生成 HLSL 代码), `GetParameterDefinitionHLSL` (生成着色器参数声明), `BuildShaderParameters`, `SetShaderParameters`。

```cpp
// 示例：将 GetMousePositionVM 函数暴露给 Niagara 脚本
// 来自: Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h
void UNiagaraDataInterfaceMousePosition::GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction &OutFunc)
{
    if (BindingInfo.Name == GetMousePositionName)
    {
        // 绑定 C++ 成员函数到 VM
        OutFunc = FVMExternalFunction::CreateUObject(this, &UNiagaraDataInterfaceMousePosition::GetMousePositionVM);
    }
    else
    {
        // 未找到的函数，报错
        UE_LOG(LogNiagara, Error, TEXT(“Could not find data interface external function in %s. Function Name: %s“), *GetPathName(), *BindingInfo.Name.ToString());
    }
}

// 示例：处理 CPU 端的每实例数据
// 来自: Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h
bool UNiagaraDataInterfaceMousePosition::PerInstanceTick(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance, float DeltaSeconds)
{
    // 此处可执行每帧的 CPU 端数据更新逻辑
    // 例如：从游戏逻辑中读取鼠标位置，存入 PerInstanceData
    return false; // 返回 true 表示数据已更新，可能触发依赖此数据的模块重新运行
}
```

### 进阶用法：HLSL 代码生成

为了让数据接口在 GPU 上工作，你需要为其每个函数生成对应的 HLSL 代码。

```cpp
// 为 “GetMousePosition” 生成 HLSL 函数定义
// 来自: Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h
FString UNiagaraDataInterfaceMousePosition::GetFunctionHLSL(const FNiagaraDataInterfaceGPUParamInfo& ParamInfo, const FNiagaraDataInterfaceGeneratedFunction& FunctionInfo, int FunctionInstanceIndex, FString& OutHLSL)
{
    if (FunctionInfo.DefinitionName == GetMousePositionName)
    {
        // 生成一个返回 FVector4f (MousePosition) 的 HLSL 函数
        return FString::Printf(TEXT(“void %s(out float4 OutMousePosition)\n{\n\tOutMousePosition = %s;\n}\n“),
            *FunctionInfo.InstanceName, *HLSLVariableName);
    }
    return FString();
}

// 为着色器参数生成声明
// 来自: Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h
void UNiagaraDataInterfaceMousePosition::GetParameterDefinitionHLSL(const FNiagaraDataInterfaceGPUParamInfo& ParamInfo, FString& OutHLSL)
{
    // 声明一个 float4 类型的着色器参数
    OutHLSL += FString::Printf(TEXT(“float4 %s;\n“), *HLSLVariableName);
}
```

## Demo 示例

以下是一个简化版的自定义数据接口，它提供一个每帧更新的常量向量。

**MyConstantDataInterface.h**
```cpp
// MyConstantDataInterface.h
#pragma once

#include “CoreMinimal.h”
#include “NiagaraDataInterface.h”
#include “MyConstantDataInterface.generated.h”

UCLASS(EditInlineNew, Category = “Constants”, meta = (DisplayName = “Constant Vector”))
class MYPLUGIN_API UMyConstantDataInterface : public UNiagaraDataInterface
{
    GENERATED_UCLASS_BODY()

public:
    // 一个可编辑的向量属性
    UPROPERTY(EditAnywhere, Category = “Parameters”)
    FVector ConstantValue;

    // UNiagaraDataInterface Interface
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc) override;
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override { return true; }

#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif

private:
    // VM 函数实现：将 ConstantValue 写入 Niagara 脚本上下文
    void GetConstantValueVM(FVectorVMExternalFunctionContext& Context);

    static const FName GetConstantValueName;
};
```

**MyConstantDataInterface.cpp**
```cpp
// MyConstantDataInterface.cpp
#include “MyConstantDataInterface.h”

const FName UMyConstantDataInterface::GetConstantValueName(“GetConstantValue”);

UMyConstantDataInterface::UMyConstantDataInterface(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer), ConstantValue(FVector::ZeroVector)
{
}

void UMyConstantDataInterface::GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc)
{
    if (BindingInfo.Name == GetConstantValueName)
    {
        OutFunc = FVMExternalFunction::CreateUObject(this, &UMyConstantDataInterface::GetConstantValueVM);
    }
}

void UMyConstantDataInterface::GetConstantValueVM(FVectorVMExternalFunctionContext& Context)
{
    // 将类属性 ConstantValue 的值设置为 Niagara 脚本的输出
    VectorVM::FUserPtrHandler<FVector> OutValue(Context);
    Context.GetParam(OutValue);
    *OutValue = ConstantValue;
}

#if WITH_EDITORONLY_DATA
void UMyConstantDataInterface::GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
    // 定义此数据接口在 Niagara 编辑器中暴露的函数签名
    FNiagaraFunctionSignature Sig;
    Sig.Name = GetConstantValueName;
    Sig.bMemberFunction = true;
    Sig.bRequiresContext = false;
    Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition(GetClass()), TEXT(“Data Interface“)));
    Sig.Outputs.Add(FNiagaraVariable(FNiagaraTypeDefinition::GetVec3Def(), TEXT(“Constant Value“)));
    OutFunctions.Add(Sig);
}
#endif
```

## 模块依赖

从 `Source/ExampleCustomDataInterface/ExampleCustomDataInterface.Build.cs` 分析：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心依赖，所有 Niagara 数据接口的基础 |
| `RenderCore` | 用于着色器参数相关类型 (`FShaderParameter`, `FShaderParametersMetadata`) |
| `RHI` | 渲染硬件接口，用于 GPU 资源操作 |

*注：`UnrealEd` 在 `PrivateDependencyModuleNames` 中，说明此模块代码仅在编辑器环境下编译（用于提供编辑器功能如函数签名），属于正常模式。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到 `UE_LOGF`，属于代码维护性更新。 |
| 2023-12-13 | `608f1437` | UNiagaraDataInterface::GetFunctions() improvements - part 1 | 改进了数据接口获取函数的内部机制，属于引擎底层重构。 |
| 2023-01-18 | `878ea7d2` | - Remove legacy binding path for Niagara data interfaces | 移除了数据接口的旧版绑定路径，清理了代码。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 常规的引擎插件目录提交。 |
| 2022-11-07 | `010079ba` | - Add method to hash a shader template file | 新增了对着色器模板文件进行哈希的方法，属于内部工具改进。 |

### 维护评价

*   **创建时间**：2021年11月，作为 UE5 早期的一部分创建。
*   **更新频率**：自创建后，更新很少。最近一次实质性更新在2023年，主要是配合 Niagara 数据接口底层 API 的重构。2026年的更新是全局性的日志宏迁移。
*   **维护状态**：**维护不活跃**。作为教学示例插件，其功能在完成后基本稳定。除非 Niagara 数据接口的底层 API 发生重大 breaking change（如2023年那次），否则它不需要频繁更新。
*   **已知问题**：没有已知的重大问题。其代码反映了 UE5.0/5.1 时期的数据接口写法，与最新版引擎的写法可能存在细微差异，但核心逻辑依然有效。
*   **推荐使用**：**强烈推荐用于学习目的**。它是理解如何创建自定义 Niagara 数据接口的官方权威示例。若要用于生产环境，建议以其为蓝本，并参考最新版引擎中其他数据接口的写法进行适配。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/ExampleCustomDataInterface)
*   [官方文档]( ) (无)
*   [测试用例]( ) (无独立的测试用例文件，但其自身就是学习用例)