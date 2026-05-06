# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.

| 属性 | 值 |
|---|---|
| 中文名 | 动态风 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图节点、骨骼网格体数据处理） |
| 模块 | `DynamicWind` (Runtime), `DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

Dynamic Wind 是一个实验性插件，旨在为 Nanite 渲染的植被（树叶、树木等）提供动态风场模拟。它通过将静态网格体（例如用 Pivot Painter 技术处理的树木）转换为骨骼网格体，并在骨骼上附加风模拟数据，使得每棵植物在全局风向和阵风作用下产生自然的摇摆动画。

该插件主要提供了编辑器端的数据导入、转换工具以及运行时子系统，用于在游戏或交互场景中实时计算并应用风力对骨骼网格体关节的影响。

## 使用场景

- 你正在制作一个包含大片森林或草地的开放世界游戏，希望树叶和草叶能随风自然飘动。
- 你使用了 Nanite 技术来渲染大量植被，但仍需保留传统骨骼动画的灵活性。
- 你需要将 Pivot Painter 纹理（树的主干、树枝的枢轴位置）转换为骨骼网格体，以便利用骨骼动画系统驱动风吹效果。
- 你希望导入自定义的骨骼关节风物理参数（如阵风衰减、模拟组）来微调不同植物的响应行为。

## 蓝图用法

本插件提供了两个可直接在蓝图中调用的静态函数，用于编辑器操作（注意：下列函数仅在设计时/Editor 中使用，不可用于运行时）。此外，还提供了可在蓝图定义的数据结构，用于描述风导入数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert Pivot Painter Tree To Skeletal Mesh` | 将带有枢轴位置纹理的静态网格体（树）转换为目标骨骼网格体，并自动建立骨骼与枢轴的对应关系 | `UDynamicWindBlueprintLibrary` |
| `Import Dynamic Wind Skeletal Data From File` | 从文件（通常是之前导出的 .wind 数据）导入风骨骼数据到目标骨骼网格体 | `UDynamicWindBlueprintLibrary` |

### 数据结构

| 结构体 | 说明 |
|---|---|
| `FDynamicWindSkeletalImportData` | 描述导入的风骨骼数据的容器，包含关节列表、模拟组列表、是否为地被草、阵风衰减参数 |
| `FDynamicWindJointImportData` | 单个关节的信息：关节名称（对应骨骼树中的骨骼名）和模拟组索引 |

### 使用示例（蓝图）

1. **将 Pivot Painter 树转换为骨骼网格体**  
   - 准备：一个静态网格体（树），一张包含枢轴位置信息的纹理（通常由 DCC 工具导出），指定 UV 通道索引。  
   - 目标：一个空白的骨骼网格体和对应的骨架资产（Skeleton）。  
   - 连接：在编辑器蓝图中调用 `ConvertPivotPainterTreeToSkeletalMesh`，输入静态网格体、纹理、UV 索引、目标骨骼网格体和骨架。  
   - 返回布尔值表示成功/失败。成功后目标骨骼网格体将获得与枢轴对应的骨骼层次，并自动应用风模拟数据。

2. **从文件导入动态风数据**  
   - 在 `FDynamicWindSkeletalImportData` 结构中填入关节名称、模拟组等参数，然后导出为文件（可通过自定义工具）。  
   - 在编辑器中调用 `ImportDynamicWindSkeletalDataFromFile`，传入目标骨骼网格体。  
   - 从文件读取数据并应用到骨骼网格体的 `UDynamicWindSkeletalData` 资产中。

## C++ 用法

### 头文件引入

```cpp
#include "DynamicWindEditorModule.h"        // 编辑器模块
#include "DynamicWindBlueprintLibrary.h"    // 蓝图库
#include "DynamicWindImportData.h"          // 导入数据结构
#include "DynamicWindSkeletalData.h"        // 运行时骨骼数据（运行时模块）
```

### 基本用法

以下代码演示了在编辑器模块启动时，如何将一株 Pivot Painter 树转换为动态风骨骼网格体（来源：`Private/DynamicWindBlueprintLibrary.cpp` 及相关文件逻辑）：

```cpp
// 假设已有：UStaticMesh* TreeMesh, UTexture2D* PivotTexture, USkeletalMesh* TargetSkelMesh, USkeleton* TargetSkeleton

bool bSuccess = UDynamicWindBlueprintLibrary::ConvertPivotPainterTreeToSkeletalMesh(
    TreeMesh,
    PivotTexture,
    0,                      // TreePivotUVIndex
    TargetSkelMesh,
    TargetSkeleton
);
if (bSuccess)
{
    // 现在 TargetSkelMesh 拥有了由枢轴纹理生成的骨骼结构及风模拟数据
    // 可将 TargetSkelMesh 用于关卡中的 Nanite 植被实例。
}
```

### 进阶用法

结合 `DynamicWind` 命名空间下的导入函数，可以在编辑器资产导入管道中自动设置风数据：

```cpp
// 从 DynamicWind::ImportSkeletalData 函数签名（在 DynamicWindImportData.h 中）

UDynamicWindSkeletalData* ImportedData = DynamicWind::ImportSkeletalData(
    *TargetSkeletalMesh,
    ImportData   // 预先填充好的 FDynamicWindSkeletalImportData 结构体
);
if (ImportedData)
{
    // ImportedData 已附加到 TargetSkeletalMesh，包含关节、模拟组、阵风衰减等参数。
    // 运行时子系统将读取此数据进行物理模拟。
}
```

## Demo 示例

以下是一个最小的编辑器工具命令行示例，展示了如何通过 C++ 在编辑器资产上下文中转换树：

**Header (MyWindTool.h)**  
```cpp
#pragma once
#include "CoreMinimal.h"
#include "DynamicWindBlueprintLibrary.h"

class FMyWindTool
{
public:
    static void ConvertTreeToWindSkeletal(const FString& InTreeMeshPath, const FString& InPivotTexturePath, const FString& OutSkelMeshPath);
};
```

**Source (MyWindTool.cpp)**  
```cpp
#include "MyWindTool.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/Skeleton.h"
#include "Engine/Texture2D.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "EditorAssetLibrary.h"

void FMyWindTool::ConvertTreeToWindSkeletal(const FString& InTreeMeshPath, const FString& InPivotTexturePath, const FString& OutSkelMeshPath)
{
    UStaticMesh* TreeMesh = LoadObject<UStaticMesh>(nullptr, *InTreeMeshPath);
    UTexture2D* PivotTex = LoadObject<UTexture2D>(nullptr, *InPivotTexturePath);
    USkeletalMesh* TargetSkel = LoadObject<USkeletalMesh>(nullptr, *OutSkelMeshPath);
    USkeleton* Skeleton = TargetSkel ? TargetSkel->GetSkeleton() : nullptr;

    if (!TreeMesh || !PivotTex || !TargetSkel || !Skeleton)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load assets"));
        return;
    }

    bool bSuccess = UDynamicWindBlueprintLibrary::ConvertPivotPainterTreeToSkeletalMesh(
        TreeMesh, PivotTex, 0, TargetSkel, Skeleton
    );

    if (bSuccess)
    {
        // 通知资产注册表刷新
        FAssetRegistryModule::AssetCreated(TargetSkel);
        TargetSkel->MarkPackageDirty();
        UEditorAssetLibrary::SaveLoadedAsset(TargetSkel, true);
        UE_LOG(LogTemp, Log, TEXT("Successfully converted tree to wind skeletal mesh."));
    }
}
```

将此工具整合到自定义菜单或脚本中即可使用。

## 模块依赖

本插件包含两个模块，其依赖关系如下：

| 模块 | 用途 |
|---|---|
| `DynamicWind` | 运行时模块，提供风模拟子系统、骨骼资产数据定义、Transform Provider 等核心逻辑。 |
| `DynamicWindEditor` | 编辑器模块，提供蓝图库、工厂、导入 UI 等编辑工具。 |

**使用者需要添加的依赖**（在你的模块的 `Build.cs` 中）：
- 如果仅使用运行时风功能，只需依赖于 `DynamicWind`。
- 如果要使用编辑器工具（如调用蓝图库函数），需要依赖 `DynamicWindEditor`，且你的模块必须是 Editor 或 DeveloperTool 类型。

另外，由于本插件是实验性的，需要确保项目设置中启用了实验性功能。

## 维护状态

### 近期更新

- 2025-12-18 `e62fa711` — [DynamicWind] 修复 DynamicWind 子系统 GT/RT 互操作中的一些线程安全问题，其中之一可能导致…
- 2025-10-14 `650ef5e2` — 移除 FDynamicWindTransformProvider 析构函数中的显式 UnregisterProvider 调用，因 FScene 注销已处理此情况。
- 2025-09-10 `89a482da` — [DynamicWind] 修复在 Instanced Skinned Mesh 上使用 DynamicWind provider 数据时可能发生的崩溃。
- 2025-09-08 `1182f57f` — 在动态风路径中实现每实例旋转与全局风向的正确结合。
- 2025-09-03 `06e395f9` — [ProceduralVegetationEditor] 设置骨骼网格体的动态风数据。

### 维护评价

- 创建于 2025 年 9 月，距今约半年，属于非常新的插件。
- 近期更新频繁（12 月、10 月、9 月），包含功能增强和错误修复。
- 修复内容涉及线程安全、崩溃、旋转计算等核心问题，说明团队正在积极完善。
- 由于仍是实验性版本（版本号 0.1），API 可能不稳定，且未经过大规模验证。
- **推荐谨慎使用**：适合对 Nanite 植被动态风有刚需的开发者，但应在充分测试后再纳入生产项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind/Tests)（可能不存在于公开仓库，请自行查看）