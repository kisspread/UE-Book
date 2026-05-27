# Chaos Cloth Asset Editor Core

> Core required functionalities for editing and creating Dataflow based Cloth Assets.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器核心 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Dataflow模板） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetEditorTools` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-01-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore) | |

## 用途

本插件提供 **基于 Dataflow 图编辑器的布料资产（Chaos Cloth Asset）编辑器** 的核心框架。它是从旧版 `ChaosClothEditor` 插件拆分而来，目的是将 USD 相关代码移出编辑器模块，同时保留完整功能。

该插件解决的核心问题是：为 Chaos 布料系统提供一个专用的可视化编辑环境，让用户能够：

- **通过 Dataflow 节点图** 构建和编辑布料资产的数据处理流程
- **双视口编辑**：2D 构造视口（查看布料的平面切割布局/Rest Space）+ 3D 预览视口（实时模拟预览）
- **交互式工具**：重网格化、权重图绘制、属性编辑、蒙皮权重传递、网格选择等
- **旧版布料资产转换**：将基于 `UClothingAssetCommon` 的旧版布料资产自动转换为新的 `UChaosClothAsset` Dataflow 格式
- **模拟控制**：暂停/恢复/重置布料物理模拟，LOD 切换，调试可视化

该插件本身不包含布料运行时逻辑，仅负责编辑器端的 UI、工具和工作流。运行时布料资产类型定义在 `ChaosClothAsset` 模块中。

## 使用场景

- 你需要为角色制作基于物理的布料效果 → 使用本编辑器创建和编辑 Chaos Cloth Asset
- 你有旧版的 `UClothingAssetCommon` 布料资产需要迁移到新的 Dataflow 工作流 → 使用 `FLegacyClothingConverter` 进行自动转换
- 你需要可视化调试布料的权重图、法线、空气动力学力等模拟数据 → 使用 3D 预览视口的调试可视化功能
- 你需要在 Dataflow 节点图中构建复杂的布料数据处理流程（导入几何体、设置模拟参数、绘制权重图等）

## 蓝图用法

本插件为纯编辑器插件，不暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 运行时 API。所有功能均通过编辑器 UI（菜单、工具栏、视口交互）和 C++ API 访问。

## C++ 用法

### 头文件引入

```cpp
// 旧版布料资产转换器（公共 API）
#include "ChaosClothAsset/LegacyClothingConverter.h"

// 编辑器命令（如需注册自定义工具）
#include "ChaosClothAsset/ClothEditorCommands.h"
```

### 基本用法 — 旧版布料资产转换

将旧版 `UClothingAssetCommon` 转换为新的 `UChaosClothAsset`。

来源文件：`Public/ChaosClothAsset/LegacyClothingConverter.h`

```cpp
#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "ClothingAsset.h"  // UClothingAssetCommon

using namespace UE::Chaos::ClothAsset;

// 方法一：创建新的布料资产
void ConvertLegacyClothAsset(const UClothingAssetCommon* LegacyAsset)
{
    FLegacyClothingConverterResult Result = FLegacyClothingConverter::Convert(
        LegacyAsset,
        TEXT("/Game/ClothAssets/"),  // 输出包路径
        TEXT("ConvertedCloth")       // 资产名称
    );

    if (Result.CreatedAsset)
    {
        UE_LOG(LogTemp, Log, TEXT("转换成功: %s"), *Result.CreatedAssetPath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("转换失败: %s"), *Result.ErrorText.ToString());
    }
}

// 方法二：转换到已存在的布料资产（就地修改）
void ConvertIntoExistingAsset(const UClothingAssetCommon* LegacyAsset,
                               UChaosClothAsset* ExistingAsset)
{
    FLegacyClothingConverterResult Result = FLegacyClothingConverter::ConvertInto(
        LegacyAsset,
        ExistingAsset
    );

    if (Result.CreatedAsset)
    {
        // ExistingAsset 已被修改，其 Dataflow 图已从旧版值烘焙完成
    }
}
```

### 进阶用法 — 转换过程细节

`FLegacyClothingConverter` 内部执行以下操作：

1. **几何体一次性烘焙**：从旧版 `FClothPhysicalMeshData` 构建布料集合，存为 Dataflow 变量覆盖（`ImportedSimClothCollection`）
2. **权重图转换**：每个旧版权重图生成一个 `WeightMapNode`，值重缩放至 [0,1]
3. **Tether 末端处理**：若旧版资产有 `TetherEndsMask`，自动切换为自定义 Tether 生成模式
4. **标量参数迁移**：通过 UProperty 反射将 `UChaosClothConfig` / `UChaosClothSharedSimConfig` 的值写入新的 Simulation 节点

> **限制**：当前仅支持 LOD 0 导入，多 LOD 旧版资产在转换后会丢失除 LOD 0 以外的所有层级。

## Demo 示例

以下展示如何通过 C++ 代码触发旧版布料资产转换（编辑器工具命令行场景）：

**ConvertLegacyCloth.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UClothingAssetCommon;

namespace UE::Chaos::ClothAsset
{
    /**
     * 将项目中所有旧版布料资产批量转换为新的 ChaosClothAsset 格式。
     */
    class FBatchClothAssetConverter
    {
    public:
        /** 扫描指定目录下的所有旧版布料资产并转换 */
        static int32 ConvertAllInPath(const FString& SourcePath,
                                       const FString& OutputPath);
    };
}
```

**ConvertLegacyCloth.cpp**
```cpp
#include "ConvertLegacyCloth.h"
#include "ChaosClothAsset/LegacyClothingConverter.h"
#include "ClothingAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"

int32 UE::Chaos::ClothAsset::FBatchClothAssetConverter::ConvertAllInPath(
    const FString& SourcePath, const FString& OutputPath)
{
    FAssetRegistryModule& AssetRegistry =
        FModuleManager::LoadModuleChecked<FAssetRegistryModule>("AssetRegistry");

    // 查找所有 UClothingAssetCommon 类型的资产
    FARFilter Filter;
    Filter.ClassPaths.Add(UClothingAssetCommon::StaticClass()->GetClassPathName());
    Filter.PackagePaths.Add(FName(*SourcePath));
    Filter.bRecursivePaths = true;

    TArray<FAssetData> AssetDatas;
    AssetRegistry.Get().GetAssets(Filter, AssetDatas);

    int32 SuccessCount = 0;
    for (const FAssetData& AssetData : AssetDatas)
    {
        const UClothingAssetCommon* LegacyAsset =
            Cast<UClothingAssetCommon>(AssetData.GetAsset());
        if (!LegacyAsset) continue;

        FLegacyClothingConverterResult Result =
            FLegacyClothingConverter::Convert(
                LegacyAsset, OutputPath, AssetData.AssetName.ToString());

        if (Result.CreatedAsset)
        {
            ++SuccessCount;
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("跳过 %s: %s"),
                *AssetData.AssetName.ToString(),
                *Result.ErrorText.ToString());
        }
    }

    UE_LOG(LogTemp, Log, TEXT("转换完成: %d/%d 成功"),
        SuccessCount, AssetDatas.Num());
    return SuccessCount;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 布料资产运行时类型定义（UChaosClothAsset、ClothCollection 等） |
| `Dataflow` | Dataflow 图编辑器框架、节点系统、EngineContext |
| `BaseCharacterFXEditor` | 角色 FX 编辑器基类框架（EdMode、Toolkit 基类） |
| `InteractiveToolsFramework` | 交互式工具框架（工具注册、输入行为、Target 系统） |
| `DynamicMesh` | 动态网格组件，用于 2D 构造视口中的可编辑网格 |
| `GeometryFramework` | 几何体框架（UDynamicMeshComponent 等） |
| `Chaos` | Chaos 物理求解器（布料模拟底层） |
| `MeshConversion` | 网格数据格式转换 |
| `ModelingComponents` | 建模组件（重网格化工具等依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `b9a938ae` | Cleanup Chaos Cloth Asset converter | 清理布料资产转换器代码 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加重新导入支持 |
| 2026-05-12 | `f1d5a018` | Dataflow : add HUD selection information to both Cloth and dataflow selection tool viewports | 为布料和 Dataflow 选择工具视口添加 HUD 选择信息 |
| 2026-04-27 | `b6b093cd` | CIS - Fixed Issue 1323734: Compile warnings in Module.ChaosClothAssetEditor.cpp | 修复编译警告（CIS Issue 1323734） |

### 维护评价

- **创建时间**：2026-01-27，从旧版 `ChaosClothEditor` 插件拆分而来，属于较新的独立模块
- **更新频率**：最近一个月内有多次功能性更新和编译修复，处于**非常活跃的开发阶段**
- **已知限制**：
  - 版本号 0.1，仍处于早期阶段
  - 旧版布料资产转换仅支持 LOD 0
  - 多个旧版 Cloth Panel Editor 命令已在 5.8 中标记为 `UE_DEPRECATED`，正迁移至 Dataflow Editor
  - 缩略图渲染器（`UChaosClothAssetThumbnailRenderer`）已标记为废弃，将移至 `ChaosClothAsset` 模块内部
- **推荐程度**：作为 Chaos 布料系统编辑端的核心组件，**必须使用**。如果你在使用 Chaos 布料（`UChaosClothAsset`），编辑器功能完全依赖本插件。当前代码质量良好，Epic 持续投入开发资源。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore/Tests)（如存在）