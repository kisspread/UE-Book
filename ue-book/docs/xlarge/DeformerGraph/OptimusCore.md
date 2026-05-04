# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (UncookedOnly), `OptimusEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph) | |

## 用途

Deformer Graph（内部代号 Optimus）是一个基于节点的可视化编辑器，用于在 GPU 上创建和执行自定义的网格变形逻辑。它解决的核心问题是：为美术和技术美术提供一种高性能、可定制、无需编写 HLSL 代码即可实现复杂网格变形（如肌肉模拟、程序化动画、物理驱动变形等）的工作流。

该插件将传统的 CPU 端网格变形逻辑转移到 GPU 计算管线中执行，利用 Compute Shader 的并行能力处理大量顶点，从而实现高性能的实时变形。用户通过连接代表数据源（如骨骼变换、顶点位置）、计算节点（数学运算、噪声生成）和输出目标（最终顶点位置）的节点来构建变形图。

## 使用场景

- **角色动画增强**：在骨骼动画基础上，添加基于物理的次级运动（如衣物、头发、肌肉抖动）。
- **程序化变形**：创建基于噪声、数学函数或运行时参数的动态网格效果（如波浪、膨胀、融化）。
- **物理模拟集成**：将简单的物理模拟结果（如布料、软体）直接应用到网格顶点上。
- **LOD 变形**：为不同 LOD 级别创建不同的变形逻辑，优化性能。
- **自定义数据驱动变形**：使用游戏逻辑数据（如速度、生命值）来驱动网格外观变化。

## 蓝图用法

Deformer Graph 主要是一个编辑器工具，其运行时实例（`UOptimusDeformerInstance`）通常由 `USkeletalMeshComponent` 或其他支持 `UMeshDeformer` 接口的组件自动管理。直接暴露给蓝图的高级 API 较少，核心交互发生在编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Deformer` | 为网格组件设置要使用的 Deformer Graph 资产。 | `UMeshDeformer` (通过组件接口) |
| `Set Variable` | 在运行时设置 Deformer Graph 中定义的变量值。 | `UOptimusDeformerInstance` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键 -> Animation -> Deformer Graph，创建一个新的 Deformer Graph 资产。
2.  **编辑图**：双击打开资产，在图表编辑器中从右键菜单添加节点（如 `Skinned Mesh` 输入、`Math` 节点、`Output` 节点）并连接它们。
3.  **应用到角色**：在角色蓝图的 `SkeletalMeshComponent` 细节面板中，找到 “Deformer” 属性，选择你创建的 Deformer Graph 资产。
4.  **运行时控制**：如果图中定义了变量（`Variable` 节点），可以在蓝图中通过获取 `SkeletalMeshComponent` 的 `Deformer Instance`，然后调用 `Set Variable` 节点来动态修改这些值。

## C++ 用法

### 头文件引入

```cpp
#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"
#include "OptimusComponentSource.h"
```

### 基本用法

以下示例展示了如何在 C++ 中为 `USkeletalMeshComponent` 设置一个 Deformer Graph。

```cpp
// 假设你已经加载了 Deformer Graph 资产
UOptimusDeformer* MyDeformerGraph = LoadObject<UOptimusDeformer>(nullptr, TEXT("/Game/MyDeformers/DG_MuscleSimulation"));

// 获取骨骼网格组件
USkeletalMeshComponent* SkelMeshComp = GetSkeletalMeshComponent();

// 设置变形器
if (SkelMeshComp && MyDeformerGraph)
{
    SkelMeshComp->SetDeformer(MyDeformerGraph);
}
```

### 进阶用法

在运行时与 Deformer Graph 的变量交互。

```cpp
// 获取变形器实例
UOptimusDeformerInstance* DeformerInstance = SkelMeshComp->GetDeformerInstance();

if (DeformerInstance)
{
    // 假设图中有一个名为 “WindStrength” 的浮点变量
    FName VariableName = TEXT("WindStrength");
    float NewWindStrength = 2.5f;

    // 查找变量并设置其值
    FOptimusValueIdentifier ValueId(EOptimusValueType::Variable, VariableName);
    FOptimusValueDescription ValueDesc;
    ValueDesc.DataType = FOptimusDataType::GetFloatType();
    ValueDesc.ValueUsage = EOptimusValueUsage::CPU;
    ValueDesc.Value.SetValue(FOptimusDataType::GetFloatType(), reinterpret_cast<const uint8*>(&NewWindStrength));

    DeformerInstance->SetValue(ValueId, ValueDesc);
}
```

## Demo 示例

以下是一个最小化的自定义数据接口示例，用于向 Deformer Graph 提供自定义数据。

**MyCustomDataInterface.h**
```cpp
#pragma once

#include "OptimusComputeDataInterface.h"
#include "MyCustomDataInterface.generated.h"

UCLASS(EditInlineNew, Category = "ComputeFramework")
class UMyCustomDataInterface : public UOptimusComputeDataInterface
{
    GENERATED_BODY()

public:
    // 从 IOptimusDataInterfaceProvider 接口实现
    virtual FString GetDisplayName() const override;
    virtual TArray<FOptimusPinProperties> GetPinProperties() const override;
    virtual FName GetCategory() const override;
    virtual void GetShaderParameters(TCHAR const* UID, FShaderParametersMetadataBuilder& OutBuilder) const override;
    virtual void GetShaderHash(FString& OutHash) const override;
    virtual void GetHLSL(FString& OutHLSL) const override;
    virtual FString GetCompiledName() const override;
    virtual UOptimusComponentSourceBinding* GetComponentBinding(const FOptimusPinTraversalContext& InContext) const override;
    virtual int32 GetDataFunctionIndexFromPin(const UOptimusNodePin* InPin) const override;

    // 自定义数据
    UPROPERTY(EditAnywhere, Category = Data)
    float MyCustomValue = 1.0f;
};
```

**MyCustomDataInterface.cpp**
```cpp
#include "MyCustomDataInterface.h"

FString UMyCustomDataInterface::GetDisplayName() const
{
    return TEXT("My Custom Data");
}

TArray<FOptimusPinProperties> UMyCustomDataInterface::GetPinProperties() const
{
    TArray<FOptimusPinProperties> Properties;
    Properties.Add(FOptimusPinProperties::MakeProperties(TEXT("Value"), EOptimusDataTypeUsageFlags::Resource));
    return Properties;
}

FName UMyCustomDataInterface::GetCategory() const
{
    return TEXT("Custom");
}

void UMyCustomDataInterface::GetShaderParameters(TCHAR const* UID, FShaderParametersMetadataBuilder& OutBuilder) const
{
    OutBuilder.AddParam<FShaderParameter>(FString::Printf(TEXT("%s_MyValue"), UID));
}

void UMyCustomDataInterface::GetShaderHash(FString& OutHash) const
{
    Super::GetShaderHash(OutHash);
    OutHash.Appendf(TEXT("%f"), MyCustomValue);
}

void UMyCustomDataInterface::GetHLSL(FString& OutHLSL) const
{
    OutHLSL.Appendf(TEXT("float %s_MyValue;\n"), *GetCompiledName());
}

FString UMyCustomDataInterface::GetCompiledName() const
{
    return TEXT("MyCustomDI");
}

UOptimusComponentSourceBinding* UMyCustomDataInterface::GetComponentBinding(const FOptimusPinTraversalContext& InContext) const
{
    // 返回此数据接口绑定的组件源，通常从上下文或节点获取
    return nullptr;
}

int32 UMyCustomDataInterface::GetDataFunctionIndexFromPin(const UOptimusNodePin* InPin) const
{
    // 根据引脚返回对应的数据函数索引
    return 0;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | 提供底层的 GPU 计算框架，Deformer Graph 在其上构建。 |
| `ControlRig` | 集成 Control Rig 系统，允许在变形图中访问和操作骨骼控制。 |
| `MeshDeformer` | 提供 `UMeshDeformer` 基类和组件集成接口。 |
| `PropertyEditor` | 用于在编辑器中自定义属性面板的显示。 |
| `SkeletalMeshDescription` | 处理骨骼网格的描述数据。 |

## 维护状态

### 近期更新

- 2025-10-03 01d1b7773814 [Deformer Graph] 避免直接替换已加载的实例设置对象，改为使用唯一名称创建新对象。
- 2025-09-15 d3a9b03ff72a [Deformer Graph] 修复了复制粘贴具有 matrix3x4 类型的资源节点会创建无引脚节点的问题。
- 2025-08-20 490a948518ad [Deformer Graph] 确保更早请求蒙皮权重配置文件，以避免在变形器激活或 LOD 变化时出现 T-Pose。

### 维护评价

Deformer Graph 是一个相对较新（约3年）但功能强大的实验性插件。从最近的提交记录来看，它仍在被 Epic Games 积极维护和改进，主要集中在修复边缘情况的 Bug 和提升工作流稳定性上。由于其标记为 `IsBetaVersion: true` 且默认未启用，表明它仍处于开发和完善阶段，可能存在一些未发现的限制或 API 变动。

**推荐使用**：对于需要高性能、可定制 GPU 变形的项目，特别是角色动画和视觉效果领域，Deformer Graph 是一个值得尝试的强大工具。但鉴于其 Beta 状态，建议在生产环境中谨慎使用，并做好应对未来 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)
- [官方文档]() (暂无)
- [测试用例]() (位于引擎测试目录，路径: `Engine/Tests/DeformerGraph/`)