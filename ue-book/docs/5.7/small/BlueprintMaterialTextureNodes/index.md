# Blueprint Material and Texture Nodes

> Adds blueprint editor-only nodes for reading textures and render targets as well as creating and modifiying Material Instance Constants

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | false (需手动启用) |
| 包含内容 | false |
| 模块 | BlueprintMaterialTextureNodes (UncookedOnly) |
| 创建时间 | 2017-10-04 |
| 年龄标签 | 👴 老古董（~8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/BlueprintMaterialTextureNodes) | |

## 用途

这个 plugin 提供了一组**编辑器专用**的蓝图节点，解决两个核心问题：

1. **在蓝图中读取纹理像素数据** — 可以对 `UTexture2D` 和 `UTextureRenderTarget2D` 进行 UV 采样，在编辑器蓝图工具中获取纹理的实际像素值，无需编写 C++ 代码。
2. **在蓝图中程序化创建和修改材质实例（MIC）** — 可以创建 `UMaterialInstanceConstant` 资产，并设置其 Scalar、Vector、Texture 参数以及渲染属性（Shading Model、Blend Mode、双面等）。

模块类型为 **UncookedOnly**，意味着这些节点只在编辑器中可用，不会被打包到最终游戏中。这是合理的，因为材质实例的创建和修改属于资产制作流程，而非运行时逻辑。

## 使用场景

- 你在做一个**程序化材质工具**（如地形纹理混合工具），需要在编辑器蓝图中读取纹理数据来决定混合权重 → 用 `Texture2D Sample UV` 和 `RenderTarget Sample UV`
- 你需要批量创建材质实例并设置参数（如批量 LOD 材质生成器）→ 用 `Create MIC` + `Set MIC Scalar/Vector/Texture Parameter`
- 你在做一个关卡设计工具，需要在放置 Actor 时动态生成材质 → 用 `Create MIC` + 各种 `Set MIC` 节点
- 你需要在编辑器工具蓝图中采样 Render Target 的某个矩形区域（如高度图读取）→ 用 `RenderTarget Sample Rectangle`

## 蓝图用法

所有节点位于蓝图搜索菜单的 **Rendering** 分类下。

### 纹理采样节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Texture2D Sample UV Editor Only` | 按 UV 坐标采样 Texture2D 的一个 texel，返回 `FLinearColor`。支持 B8G8R8A8 和 FloatRGBA 格式，也支持从纹理源数据回退读取 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `RenderTarget Sample UV Editor Only` | 按 UV 坐标采样 RenderTarget2D 的一个像素，返回 `FLinearColor` | `UBlueprintMaterialTextureNodesBPLibrary` |
| `RenderTarget Sample Rectangle Editor Only` | 采样 RenderTarget2D 的一个矩形区域，返回 `TArray<FLinearColor>` | `UBlueprintMaterialTextureNodesBPLibrary` |

### 材质实例创建与修改节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MIC Editor Only` | 基于父材质创建一个新的 MaterialInstanceConstant 资产 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Scalar Parameter Editor Only` | 设置 MIC 的标量参数值 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Vector Parameter Editor Only` | 设置 MIC 的向量参数值 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Texture Parameter Editor Only` | 设置 MIC 的纹理参数值 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Shading Model Editor Only` | 覆盖 MIC 的 Shading Model | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Blend Mode Editor Only` | 覆盖 MIC 的 Blend Mode | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Two Sided Editor Only` | 覆盖 MIC 的双面设置 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC IsThinSurface Editor Only` | 覆盖 MIC 的 Thin Surface 设置 | `UBlueprintMaterialTextureNodesBPLibrary` |
| `Set MIC Dithered LOD Editor Only` | 覆盖 MIC 的 Dithered LOD Transition 设置 | `UBlueprintMaterialTextureNodesBPLibrary` |

### 使用示例（蓝图描述）

**示例 1：读取纹理像素**

1. 创建一个 Editor Utility Blueprint（父类 `EditorUtilityObject` 或 `Actor`）
2. 添加一个 `UTexture2D` 类型的变量 `MyTexture`
3. 连接：`MyTexture` + `UV (0.5, 0.5)` → `Texture2D Sample UV Editor Only` → 输出 `FLinearColor`
4. 可以用 `Break Linear Color` 查看 R/G/B/A 各通道值

**示例 2：程序化创建材质实例**

1. 添加一个 `UMaterialInterface*` 变量 `BaseMaterial`
2. `BaseMaterial` → `Create MIC Editor Only`（Name 参数默认为 `"MIC_"`）→ 输出 `MIC` 变量
3. `MIC` + `"Metallic"` + `0.8` → `Set MIC Scalar Parameter Editor Only`
4. `MIC` + `"BaseColor"` + `(1, 0, 0, 1)` → `Set MIC Vector Parameter Editor Only`
5. `MIC` + `"NormalMap"` + Texture → `Set MIC Texture Parameter Editor Only`
6. 结果：在 Content Browser 中与父材质同目录下生成了新的 MIC 资产，并自动在浏览器中定位

**示例 3：批量采样 Render Target 区域**

1. 获取一个 `UTextureRenderTarget2D`（如场景捕获组件的输出）
2. 用 `RenderTarget Sample Rectangle Editor Only`，传入 `InRect = (X1, Y1, X2, Y2)` 作为 `FLinearColor` 的 (R, G, B, A)
3. 输出 `TArray<FLinearColor>`，可遍历获取区域内所有像素值

## C++ 用法

### 头文件引入

```cpp
#include "BlueprintMaterialTextureNodesBPLibrary.h"
```

### 基本用法

由于所有函数都是 `UBlueprintFunctionLibrary` 的静态方法，在 C++ 中也可以直接调用：

```cpp
// 采样 Texture2D
UTexture2D* Texture = LoadObject<UTexture2D>(nullptr, TEXT("/Game/MyTexture"));
FLinearColor PixelValue = UBlueprintMaterialTextureNodesBPLibrary::Texture2D_SampleUV_EditorOnly(Texture, FVector2D(0.5f, 0.5f));

// 创建材质实例
UMaterialInterface* ParentMaterial = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/MyMaterial"));
UMaterialInstanceConstant* MIC = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(ParentMaterial, TEXT("MIC_NewInstance"));

// 设置材质参数
UBlueprintMaterialTextureNodesBPLibrary::SetMICScalarParam_EditorOnly(MIC, TEXT("Roughness"), 0.5f);
UBlueprintMaterialTextureNodesBPLibrary::SetMICVectorParam_EditorOnly(MIC, TEXT("BaseColor"), FLinearColor(1, 0, 0, 1));
```

> 来源：`Source/BlueprintMaterialTextureNodes/Private/BlueprintMaterialTextureNodesBPLibrary.cpp`

### 进阶用法

`CreateMIC_EditorOnly` 支持两种命名模式：

```cpp
// 模式 1：仅名称 — 在父材质同目录下创建，自动去重
UMaterialInstanceConstant* MIC1 = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(ParentMaterial, TEXT("MIC_Variant"));

// 模式 2：完整路径 — 指定目标路径
UMaterialInstanceConstant* MIC2 = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(ParentMaterial, TEXT("/Game/Materials/MIC_Specific"));
```

材质属性覆盖（使用 `BasePropertyOverrides`）：

```cpp
UBlueprintMaterialTextureNodesBPLibrary::SetMICShadingModel_EditorOnly(MIC, MSM_DefaultLit);
UBlueprintMaterialTextureNodesBPLibrary::SetMICBlendMode_EditorOnly(MIC, BLEND_Translucent);
UBlueprintMaterialTextureNodesBPLibrary::SetMICTwoSided_EditorOnly(MIC, true);
UBlueprintMaterialTextureNodesBPLibrary::SetMICIsThinSurface_EditorOnly(MIC, true);
UBlueprintMaterialTextureNodesBPLibrary::SetMICDitheredLODTransition_EditorOnly(MIC, true);
```

### 注意事项

- 所有函数都有 `#if WITH_EDITOR` 保护，打包后调用会输出错误日志并返回默认值
- 纹理采样支持 `PF_B8G8R8A8` 和 `PF_FloatRGBA` 格式，其他格式会尝试从纹理源数据读取
- Render Target 采样仅支持 `RTF_RGBA8`、`RTF_RGBA16f`、`RTF_RGBA32f` 三种四通道格式
- `UpdateMIC` 函数内部标记了 `TODO`：材质编辑器窗口可能不会自动刷新

## Demo 示例

### 最小 C++ 模块示例

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Engine",
    "BlueprintMaterialTextureNodes",
});
```

**示例代码：**

```cpp
// MyMaterialTool.h
#pragma once
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyMaterialTool.generated.h"

UCLASS()
class UMyMaterialTool : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 在蓝图中调用：基于父材质创建一个红色材质实例
    UFUNCTION(BlueprintCallable, Category = "MaterialTool")
    static UMaterialInstanceConstant* CreateRedMIC(UMaterialInterface* ParentMaterial, const FString& Name)
    {
        // 创建 MIC
        UMaterialInstanceConstant* MIC = UBlueprintMaterialTextureNodesBPLibrary::CreateMIC_EditorOnly(ParentMaterial, Name);
        if (MIC)
        {
            // 设置红色基础色
            UBlueprintMaterialTextureNodesBPLibrary::SetMICVectorParam_EditorOnly(MIC, TEXT("BaseColor"), FLinearColor(1, 0, 0, 1));
        }
        return MIC;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Engine` | 核心引擎（公共依赖） |
| `Core` | 基础类型和工具 |
| `CoreUObject` | UObject 系统 |
| `ImageCore` | 图像处理（纹理源数据读取） |
| `RHI` | 渲染硬件接口（Render Target 读取） |
| `UnrealEd` | 编辑器功能（资产创建、浏览器定位） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `8396b18` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n | 批量 API 符号导出规范化，非功能性改动 |
| 2024-10-22 | `98a8e0e` | Removed lots of UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理已废弃的头文件兼容宏，非功能性改动 |
| 2024-01-29 | `f85866d` | Updated CreateMIC_EditorOnly to be consistent with path handling from KismetRenderingLibrary | 修复路径处理逻辑，允许在插件目录下创建资产，不再强制 `/Game/` 前缀 |

### 维护评价

- **创建时间**：2017 年 10 月，已有约 8 年历史
- **最近更新**：2025 年 5 月有编译层面上的更新，但最近一次功能性更新是 2024 年 1 月
- **维护状态**：**维护不活跃** — 近 2 年内无实质性功能更新，仅有编译器/头文件层面的清理
- **稳定程度**：功能非常稳定且简单，代码量小，不太需要频繁更新
- **已知问题**：源码中标注了 `UpdateMIC` 的 TODO — 材质编辑器窗口不会自动刷新
- **推荐使用**：✅ 推荐。这是一个小巧实用的编辑器工具节点集，虽然不常更新，但功能完整且由 Epic 官方维护。适合需要在蓝图编辑器工具中读取纹理或批量创建材质实例的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/BlueprintMaterialTextureNodes)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 测试用例：无（plugin 目录内未包含测试文件）
