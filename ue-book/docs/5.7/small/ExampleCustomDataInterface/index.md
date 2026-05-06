# Niagara Example Custom DataInterface

> This plugin contains C++ example content that shows how to write your own data interface for Niagara. Check out the plugin folder Engine/Plugins/FX/ExampleCustomDataInterface for the source files.

| 属性 | 值 |
|---|---|
| 中文名 | 鼠标位置数据接口示例 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ExampleCustomDataInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/ExampleCustomDataInterface) | |

## 用途

Niagara 粒子系统支持通过“数据接口（DataInterface）”从外部获取自定义数据，例如鼠标位置、物理碰撞、网络数据等。该插件提供了一个最小化的官方示例，展示了如何编写一个自定义 Niagara 数据接口（`UNiagaraDataInterfaceMousePosition`），该接口在每帧更新时从虚幻引擎获取鼠标在视图中的位置，并暴露给 Niagara 粒子系统使用。

**为什么需要这个插件？**  
- 它是官方提供的学习模板，开发者可以参照它快速创建自己的数据接口，避免从零研究 Niagara 内部机制。  
- 提供了完整的 CPU 和 GPU 端支持（包含 HLSL 代码生成），展示了数据接口的标准架构。

## 使用场景

- 你需要让粒子特效跟随鼠标移动（如鼠标轨迹、点击爆炸、瞄准指示器等）。  
- 你想学习如何为 Niagara 编写自定义数据接口，为后续扩展复杂数据源（如网络/物理/音频）打基础。  
- 你正在开发需要从游戏逻辑（如角色血量、游戏状态）实时驱动粒子的功能，而内置数据接口不足以满足需求。

## 蓝图用法

该插件不暴露任何 BlueprintCallable 函数。自定义数据接口的用法是在 Niagara 编辑器中作为“数据接口”节点使用。

### 在 Niagara 系统中使用

1. 创建一个 Niagara 系统（或打开现有系统）。  
2. 在 Niagara 编辑器“参数”面板中，添加一个“数据接口”参数，类型选择 `MousePosition Query`（显示名称由插件定义）。  
3. 在模块图中将此数据接口拖入，获取其 `Get Mouse Position` 函数，连接至 Position 或其他属性即可让粒子跟随鼠标。

> 注意：该示例数据接口只有 CPU 模拟可用（`CanExecuteOnTarget` 返回 true，但 HLSL 支持用于 GPU，不过实际使用建议在 CPU 模拟中测试）。在 Niagara 编辑器中，你只能将其绑定到 CPU 发射器。

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraDataInterfaceMousePosition.h"
```

### 基本用法

以下代码展示了如何创建一个自定义数据接口的子类（参考插件源码中的完整实现）。

**来源文件：** `Engine/Plugins/FX/ExampleCustomDataInterface/Source/ExampleCustomDataInterface/Private/NiagaraDataInterfaceMousePosition.h`

```cpp
// 你的自定义数据接口类
UCLASS(EditInlineNew, Category = "MyDataInterfaces", meta = (DisplayName = "My Custom Data"))
class UMyCustomDataInterface : public UNiagaraDataInterface
{
    GENERATED_BODY()

public:
    // 必须实现的核心函数：
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc) override;
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override { return true; } // 支持 CPU 和 GPU
    virtual int32 PerInstanceDataSize() const override;
    virtual bool InitPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance) override;
    virtual void DestroyPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance) override;
    virtual bool PerInstanceTick(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance, float DeltaSeconds) override;
    virtual void ProvidePerInstanceDataForRenderThread(void* DataForRenderThread, void* PerInstanceData, const FNiagaraSystemInstanceID& SystemInstance) override;

#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
    virtual bool AppendCompileHash(FNiagaraCompileHashVisitor* InVisitor) const override;
    virtual bool GetFunctionHLSL(const FNiagaraDataInterfaceGPUParamInfo& ParamInfo, const FNiagaraDataInterfaceGeneratedFunction& FunctionInfo, int FunctionInstanceIndex, FString& OutHLSL) override;
    virtual void GetParameterDefinitionHLSL(const FNiagaraDataInterfaceGPUParamInfo& ParamInfo, FString& OutHLSL) override;
#endif

    virtual void BuildShaderParameters(FNiagaraShaderParametersBuilder& ShaderParametersBuilder) const override;
    virtual void SetShaderParameters(const FNiagaraDataInterfaceSetShaderParametersContext& Context) const override;

    // VM 函数（CPU 端暴露给脚本）
    void MyCustomFunctionVM(FVectorVMExternalFunctionContext& Context);

private:
    static const FName MyCustomFunctionName;
};
```

### 进阶用法：实现自定义数据更新

参考 `UNiagaraDataInterfaceMousePosition::PerInstanceTick`，在每帧更新实例数据（如鼠标位置）并传递给渲染线程（`ProvidePerInstanceDataForRenderThread`）。典型流程：

1. 在 `PerInstanceTick` 中从 `UGameViewportClient` 获取鼠标屏幕位置，存储到 `PerInstanceData`（一个自定义结构体）。  
2. 在 `ProvidePerInstanceDataForRenderThread` 中将该数据拷贝到 GPU 可用缓冲区。  
3. 在 `GetFunctionHLSL` 中生成 HLSL 代码，使用 `SHADER_PARAMETER` 声明的参数读取该数据。

## Demo 示例

以下是一个完整的最小化自定义数据接口（仅 CPU 模拟），展示从游戏实例获取任意 float 值并暴露给 Niagara。

### MySimpleDataInterface.h

```cpp
#pragma once

#include "NiagaraDataInterface.h"
#include "NiagaraDataInterface.generated.h"

UCLASS(EditInlineNew, Category = "MyData", meta = (DisplayName = "Simple Float Data"))
class USimpleFloatDataInterface : public UNiagaraDataInterface
{
    GENERATED_BODY()

public:
    USimpleFloatDataInterface();
    virtual void PostInitProperties() override;

    // Niagara DataInterface 接口
    virtual void GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc) override;
    virtual bool CanExecuteOnTarget(ENiagaraSimTarget Target) const override { return true; }
    virtual int32 PerInstanceDataSize() const override;
    virtual bool InitPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance) override;
    virtual void DestroyPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance) override;
    virtual bool PerInstanceTick(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance, float DeltaSeconds) override;

#if WITH_EDITORONLY_DATA
    virtual void GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const override;
#endif

    void GetMyFloatVM(FVectorVMExternalFunctionContext& Context);

private:
    static const FName GetMyFloatName;
};
```

### MySimpleDataInterface.cpp

```cpp
#include "MySimpleDataInterface.h"
#include "NiagaraTypes.h"
#include "NiagaraSystemInstance.h"

const FName USimpleFloatDataInterface::GetMyFloatName = GET_MEMBER_NAME_CHECKED(USimpleFloatDataInterface, GetMyFloatName);

USimpleFloatDataInterface::USimpleFloatDataInterface()
{
    // 注册默认实例数据
}

void USimpleFloatDataInterface::PostInitProperties()
{
    Super::PostInitProperties();
}

struct FSimpleFloatData
{
    float FloatValue;
};

int32 USimpleFloatDataInterface::PerInstanceDataSize() const
{
    return sizeof(FSimpleFloatData);
}

bool USimpleFloatDataInterface::InitPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance)
{
    FSimpleFloatData* Data = new(PerInstanceData) FSimpleFloatData();
    Data->FloatValue = 0.0f;
    return true;
}

void USimpleFloatDataInterface::DestroyPerInstanceData(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance)
{
    FSimpleFloatData* Data = static_cast<FSimpleFloatData*>(PerInstanceData);
    Data->~FSimpleFloatData();
}

bool USimpleFloatDataInterface::PerInstanceTick(void* PerInstanceData, FNiagaraSystemInstance* SystemInstance, float DeltaSeconds)
{
    FSimpleFloatData* Data = static_cast<FSimpleFloatData*>(PerInstanceData);
    // 示例：每帧递增（实际可从游戏状态获取）
    Data->FloatValue += DeltaSeconds;
    return true;
}

#if WITH_EDITORONLY_DATA
void USimpleFloatDataInterface::GetFunctionsInternal(TArray<FNiagaraFunctionSignature>& OutFunctions) const
{
    FNiagaraFunctionSignature Sig;
    Sig.Name = GetMyFloatName;
    Sig.bMemberFunction = true;
    Sig.bRequiresContext = false;
    Sig.Inputs.Add(FNiagaraVariable(FNiagaraTypeDefinition::GetFloatDef(), TEXT("Float")));
    Sig.Outputs.Add(FNiagaraVariable(FNiagaraTypeDefinition::GetFloatDef(), TEXT("OutFloat")));
    Sig.SetDescription(TEXT("Returns a per-instance float value"));
    OutFunctions.Add(Sig);
}
#endif

void USimpleFloatDataInterface::GetVMExternalFunction(const FVMExternalFunctionBindingInfo& BindingInfo, void* InstanceData, FVMExternalFunction& OutFunc)
{
    if (BindingInfo.Name == GetMyFloatName)
    {
        OutFunc = FVMExternalFunction::CreateStatic(&USimpleFloatDataInterface::GetMyFloatVM);
    }
}

void USimpleFloatDataInterface::GetMyFloatVM(FVectorVMExternalFunctionContext& Context)
{
    VectorVM::FExternalFuncRegisterHandler<float> OutFloat(Context);
    FSimpleFloatData* InstanceData = (FSimpleFloatData*)Context.GetInstanceData();
    *OutFloat.GetDest() = InstanceData->FloatValue;
}
```

将此模块添加到插件，并在 Niagara 系统中使用即可。

## 模块依赖

若你的模块需要引用此插件的类（如继承 `UNiagaraDataInterfaceMousePosition`），请在 Build.cs 中添加：

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心 Niagara 框架，提供数据接口基类 |
| `UnrealEd` | 编辑器模块，仅当你的数据接口需要编辑器特定功能时（预览、编译等） |

> 实际示例插件内部依赖了 `UnrealEd`（用于编辑器中编译和测试），但生产插件通常只需要 `Niagara` 即可。建议你的自定义数据接口模块仅添加 `Niagara` 到公共依赖，将 `UnrealEd` 保留为私有依赖（使用 `PrivateDependencyModuleNames`）。

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2023-12-13 | `608f1437` | UNiagaraDataInterface::GetFunctions() improvements - part 1 |
| 2023-01-18 | `878ea7d2` | - Remove legacy binding path for Niagara data interfaces |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] (批量文件改动) |
| 2022-11-07 | `010079ba` | - Add method to hash a shader template file |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. |

### 维护评价

- **创建时间**：2022-10-21，距今约 3 年。  
- **最近更新**：2023-12-13，距今已超过 1 年无实质性功能更新。  
- **活跃度**：不活跃。最后一次更新属于 Niagara 框架的通用改进，未针对此示例插件本身新增内容。  
- **结论**：该插件属于“一次性学习资源”，作者未计划持续维护。核心代码仍可用于 UE 5.5+，但若有底层 API 变更可能需要手动适配。推荐仅作为学习参考，生产项目谨慎直接依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/ExampleCustomDataInterface)  
- [官方文档（Niagara 数据接口概述）](https://docs.unrealengine.com/5.7/en-US/niagara-data-interfaces-reference/)  
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/FX/ExampleCustomDataInterface/Source/ExampleCustomDataInterface)（无独立测试文件，仅源码）