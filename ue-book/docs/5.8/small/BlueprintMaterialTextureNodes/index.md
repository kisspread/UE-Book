# Blueprint Material Texture Nodes

> Adds blueprint editor-only nodes for reading textures and render targets as well as creating and modifiying Material Instance Constants

| 属性 | 值 |
|---|---|
| 中文名 | 材质纹理蓝图节点 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintMaterialTextureNodes` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/BlueprintMaterialTextureNodes) | |

## 用途

该插件提供了一系列**仅在编辑器中可用**的蓝图函数，旨在简化和加速材质工作流程。它主要解决以下问题：
1.  **纹理数据读取**：允许在编辑器蓝图中直接以 UV 坐标采样 `Texture2D` 和 `TextureRenderTarget2D` 的像素数据，便于进行运行时材质调试、程序化内容生成或数据检查。
2.  **动态材质实例管理**：提供创建、修改（标量、向量、纹理参数，以及着色模型、混合模式等属性）`MaterialInstanceConstant (MIC)` 的蓝图节点。这使得美术和设计师可以在编辑器中通过蓝图工具或简单的 UI 快速迭代和批量生成材质变体，而无需手动在属性面板中操作。

简而言之，该插件将部分底层编辑器 API 暴露给蓝图，增强了编辑器内的程序化和工具化能力。

## 使用场景

-   你是一个技术美术，需要在编辑器内快速创建一个材质参数修改工具 → 用 `CreateMIC_EditorOnly` 和 `SetMIC*` 系列节点。
-   你正在开发一个编辑器插件，需要读取一张渲染目标（Render Target）中的数据用于后处理或数据可视化 → 用 `RenderTarget_SampleUV_EditorOnly`。
-   你想要批量为大量静态网格物体生成带有不同纹理或颜色参数的材质实例 → 用蓝图循环调用创建和设置MIC的节点。

## 蓝图用法

所有节点均位于蓝图编辑器下拉菜单的 **Rendering** 分类中，且名称后缀通常包含 “Editor Only”。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMIC_EditorOnly` | 从给定的材质接口创建一个新的材质实例常量资产。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICScalarParam_EditorOnly` | 设置材质实例中的标量参数值。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICVectorParam_EditorOnly` | 设置材质实例中的向量参数值。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICTextureParam_EditorOnly` | 设置材质实例中的纹理参数。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICShadingModel_EditorOnly` | 覆盖材质实例的着色模型。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICBlendMode_EditorOnly` | 覆盖材质实例的混合模式。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICTwoSided_EditorOnly` | 覆盖材质实例的“双面”设置。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICIsThinSurface_EditorOnly` | 覆盖材质实例的“薄表面”设置。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `SetMICDitheredLODTransition_EditorOnly` | 覆盖材质实例的“抖动LOD过渡”设置。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Texture2D_SampleUV_EditorOnly` | 通过 UV 坐标从 Texture2D 采样一个线性颜色值。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `RenderTarget_SampleUV_EditorOnly` | 通过 UV 坐标从纹理渲染目标采样一个线性颜色值。 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `RenderTarget_SampleRectangle_EditorOnly` | 从纹理渲染目标的一个矩形区域采样一组值。 | `UBlueprintMaterialTextureNodesBPLibrary` |

### 使用示例（蓝图描述）

1.  **动态创建和修改材质实例**：
    *   获取一个基础材质的引用（例如 `Material` 变量）。
    *   拖拽该变量，连接到 `CreateMIC_EditorOnly` 节点的 `Material` 引脚。设置一个 `Name`（例如 “MIC_Car_Paint”），执行节点后会在内容浏览器生成对应的MIC资产。
    *   将 `CreateMIC_EditorOnly` 节点的返回值（MIC引用）连接到 `SetMICScalarParam_EditorOnly` 节点的 `Material` 引脚。
    *   设置 `ParamName` 为材质中已有的参数名（如 “Roughness”），设置 `Value`（例如 0.5）。执行该节点即可修改MIC的粗糙度参数。

2.  **在编辑器中读取渲染目标数据**：
    *   获取一个 `TextureRenderTarget2D` 资产的引用。
    *   拖拽该变量，连接到 `RenderTarget_SampleUV_EditorOnly` 节点的 `InRenderTarget` 引脚。
    *   设置 `UV` 坐标（例如 (0.5, 0.5) 代表中心点），执行节点后，其输出的 `FLinearColor` 即为该点采样的颜色值。可以在蓝图中进一步处理或显示此数据。

## C++ 用法

### 头文件引入

```cpp
#include “BlueprintMaterialTextureNodesBPLibrary.h”
```

### 基本用法

该插件主要为蓝图设计，其C++接口同样是静态函数。以下示例展示如何在C++中调用这些函数（例如在编辑器工具或自定义命令中）。
```cpp
// 假设你已经有一个 UMaterialInterface* BaseMaterial 和一个 UTexture2D* SomeTexture
// 来源：基于 Public/BlueprintMaterialTextureNodesBPLibrary.h 中的函数声明推断

// 1. 创建一个新的材质实例常量
UMaterialInstanceConstant* NewMIC = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(BaseMaterial, TEXT(“MIC_FromCpp”));

// 2. 为新的MIC设置一个标量参数
UBlueprintMaterialTextureNodesBPLibrary::SetMICScalarParam_EditorOnly(NewMIC, TEXT(“Metallic”), 1.0f);

// 3. 为新的MIC设置一个纹理参数
UBlueprintMaterialTextureNodesBPLibrary::SetMICTextureParam_EditorOnly(NewMIC, TEXT(“BaseColorTexture”), SomeTexture);

// 4. 从一个Texture2D上采样颜色值（仅编辑器）
FLinearColor SampledColor = UBlueprintMaterialTextureNodesBPLibrary::Texture2D_SampleUV_EditorOnly(SomeTexture, FVector2D(0.5f, 0.5f));
UE_LOG(LogTemp, Log, TEXT(“Sampled Color: %s”), *SampledColor.ToString());
```

### 进阶用法

组合使用这些函数可以实现更复杂的编辑器批处理逻辑，例如遍历一个材质参数列表并批量应用到新的MIC上。
```cpp
// 假设有一个TArray<FString> ParamNames 和 TArray<float> ParamValues
UMaterialInstanceConstant* BatchMIC = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(MyMaterial, TEXT(“BatchMIC”));

for (int32 i = 0; i < ParamNames.Num(); ++i)
{
    UBlueprintMaterialTextureNodesBPLibrary::SetMICScalarParam_EditorOnly(BatchMIC, ParamNames[i], ParamValues[i]);
}
```

## Demo 示例

一个最小的编辑器工具类示例，演示如何在C++中结合使用该插件的功能。

**MyMaterialTools.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “UObject/NoExportTypes.h”
#include “MyMaterialTools.generated.h”

UCLASS(BlueprintType)
class UMyMaterialTools : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = “Material Tools”)
    static void CreateAndModifyMIC(UMaterialInterface* BaseMaterial, UTexture2D* TextureParam);
};
```

**MyMaterialTools.cpp**
```cpp
#include “MyMaterialTools.h”
#include “BlueprintMaterialTextureNodesBPLibrary.h”

void UMyMaterialTools::CreateAndModifyMIC(UMaterialInterface* BaseMaterial, UTexture2D* TextureParam)
{
    if (!BaseMaterial)
    {
        UE_LOG(LogTemp, Warning, TEXT(“BaseMaterial is null.”));
        return;
    }

    // 创建一个新的MIC
    UMaterialInstanceConstant* NewMIC = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(BaseMaterial, TEXT(“DemoMIC”));
    if (!NewMIC)
    {
        UE_LOG(LogTemp, Warning, TEXT(“Failed to create MIC.”));
        return;
    }

    // 设置一些参数
    UBlueprintMaterialTextureNodesBPLibrary::SetMICScalarParam_EditorOnly(NewMIC, TEXT(“ScalarParam”), 0.75f);
    UBlueprintMaterialTextureNodesBPLibrary::SetMICVectorParam_EditorOnly(NewMIC, TEXT(“ColorParam”), FLinearColor::Red);

    if (TextureParam)
    {
        UBlueprintMaterialTextureNodesBPLibrary::SetMICTextureParam_EditorOnly(NewMIC, TEXT(“TextureParam”), TextureParam);
    }

    // 可选：从一个渲染目标采样（假设你有一个 RenderTarget 引用）
    // FLinearColor Data = UBlueprintMaterialTextureNodesBPLibrary::RenderTarget_SampleUV_EditorOnly(MyRenderTarget, FVector2D::ZeroVector);
    // UE_LOG(LogTemp, Log, TEXT(“RT Sampled: %s”), *Data.ToString());

    UE_LOG(LogTemp, Log, TEXT(“MIC ‘%s’ created and modified successfully.”), *NewMIC->GetName());
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用工具更新头文件，确保 DLL 导出声明正确。 |
| 2024-10-22 | `98a8e0e0` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 移除了大量已弃用的包含顺序宏，适应新引擎版本。 |
| 2024-01-30 | `f85866d7` | BlueprintMaterialTextureNodes: Updated CreateMIC_EditorOnly to be consistent with the path handling | 更新了 `CreateMIC_EditorOnly` 函数的路径处理逻辑，使其更一致。 |
| 2023-11-29 | `5dfe9647` | PR #11095: Fix sampling UV on rectangular textures | 修复了对非正方形纹理进行 UV 采样时的问题。 |
| 2023-03-29 | `ffe45866` | clean up code using GetMipData without checking return value | 清理了未检查 `GetMipData` 返回值的代码，提升健壮性。 |

### 维护评价

-   **年龄**：插件创建于 2017 年，已超过 5 年。
-   **活跃度**：最近一次功能性更新在 2023 年底（修复 UV 采样），2024 和 2025 年的更新主要是代码维护和适配新引擎版本。属于**低活跃度维护**状态。
-   **状态**：插件功能稳定，但核心 API 长期未增加新特性。近期更新集中在代码清理和编译兼容性，表明它仍被保留在引擎代码库中，但并非开发重点。
-   **推荐**：适用于需要在**编辑器内**进行特定材质和纹理操作的工具或工作流。由于所有函数都标记为 “Editor Only”，**不能在打包后的游戏中使用**。如果项目有此类编辑器扩展需求，可以使用，但需知其功能已基本定型，未来可能只会有兼容性修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/BlueprintMaterialTextureNodes)