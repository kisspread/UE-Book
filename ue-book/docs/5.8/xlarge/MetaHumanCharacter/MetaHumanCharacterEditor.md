# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 角色编辑器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、灯光场景、预设资产） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHumanCharacter 是 Epic 为 UE5 打造的**下一代 MetaHuman 角色资产创建与编辑系统**。它取代了原先依赖 MetaHuman Creator 云端服务的工作流，将完整的角色创建流程内置到引擎编辑器中。

该插件解决的核心问题：

1. **参数化角色建模**：提供基于身份模型（Identity Model）的参数化面部和身体创建，用户可以通过操控控制点、混合预设角色或导入外部数据来定义角色外观
2. **全流水线编辑**：从面部雕刻、身体塑形、皮肤材质编辑、牙齿/睫毛调整，到服装穿戴（Wardrobe）、资产打包（Pipeline Build），提供端到端的角色制作工具
3. **多源导入**：支持从 DNA 文件、MetaHuman Identity 资产、自定义网格模板等多种来源导入角色数据
4. **纹理合成**：集成本地纹理合成模型，根据角色的 UV 参数生成高分辨率面部纹理（包括基础颜色、法线、粗糙度等）
5. **导出能力**：支持导出为 DCC 格式（Maya/Blender）、DNA 文件、几何体网格、材质资产等多种格式
6. **编辑器集成**：提供完整的自定义编辑器模式，包含专用视口、灯光环境、动画预览、渲染质量控制等

这个插件是 MetaHuman 生态系统在引擎端的核心，它使得角色创建不再需要外部工具和云服务，全部在 UE 编辑器内完成。

## 使用场景

- 你在制作需要高保真数字人物的游戏或影视项目 → 使用 MetaHuman Creator 创建并编辑角色
- 你需要从已有的 DNA 文件（如从 MetaHuman Creator 旧版导出）创建可编辑的角色 → 使用 Import From DNA 工具导入
- 你需要基于扫描数据或自定义模型快速生成 MetaHuman → 使用 Import From Template 工具
- 你需要为角色搭配服装和配饰 → 使用 Wardrobe 工具管理服装系统
- 你需要调整角色的皮肤色调、雀斑、妆容等外观细节 → 使用 Skin 工具
- 你需要将编辑好的角色打包为可在运行时使用的蓝图资产 → 使用 Pipeline 工具执行构建
- 你需要将角色导出到 Maya 或 Blender 进行进一步动画制作 → 使用 DCC Export
- 你需要参数化地调整角色身体比例（身高、胸围、腰围等） → 使用 Body Model 工具的参数化约束

## 蓝图用法

该插件的核心蓝图 API 集中在 `UMetaHumanCharacterEditorSubsystem`（编辑器子系统）和 `UMetaHumanCharacterExportBlueprintLibrary`（导出函数库）中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TryAddObjectToEdit` | 注册一个 MetaHuman 角色进行编辑，返回是否成功 | `UMetaHumanCharacterEditorSubsystem` |
| `IsObjectAddedForEditing` | 检查角色是否已注册用于编辑 | `UMetaHumanCharacterEditorSubsystem` |
| `ExportDCC` | 将角色导出为 DCC 工具可用的包 | `UMetaHumanCharacterExportBlueprintLibrary` |
| `ExportDNA` | 导出头部和/或身体的 DNA 资产到项目内容中 | `UMetaHumanCharacterExportBlueprintLibrary` |
| `ExportGeometry` | 导出骨骼网格体资产到项目内容中 | `UMetaHumanCharacterExportBlueprintLibrary` |
| `ExportMaterials` | 导出材质为持久化 MIC 资产到项目内容中 | `UMetaHumanCharacterExportBlueprintLibrary` |
| `ExportPosedDNA` | 导出先前 ConformToTargetMeshes 生成的组合姿势 DNA | `UMetaHumanCharacterExportBlueprintLibrary` |

### 使用示例（蓝图描述）

**导出角色为 DCC 包**：

1. 加载或获取一个 `UMetaHumanCharacter` 资产引用
2. 创建一个 `FMetaHumanDCCExportParams` 结构体
3. 设置 `ExternalPath` 为输出文件夹路径
4. 可选设置 `bBakeMakeUp`（烘焙妆容到面部纹理）、`bCompressInZipFile`（压缩为 ZIP）
5. 调用 `UMetaHumanCharacterExportBlueprintLibrary::ExportDCC`

**导出 DNA 文件**：

1. 获取 `UMetaHumanCharacter` 资产引用
2. 创建 `FMetaHumanDNAExportParams` 结构体
3. 设置 `ProjectPath`（如 "/Game/MetaHumans"）和/或 `ExternalPath`（磁盘路径）
4. 选择导出 `bDNAHead` 和/或 `bDNABody`
5. 调用 `UMetaHumanCharacterExportBlueprintLibrary::ExportDNA`

**Python 脚本示例**（来自源码注释）：

```python
import unreal
character = unreal.load_asset("/Game/MetaHumans/MyCharacter")
params = unreal.MetaHumanDCCExportParams()
params.external_path = "D:/Export/MyCharacter"
unreal.MetaHumanCharacterExportBlueprintLibrary.export_dcc(character, params)
```

## C++ 用法

### 头文件引入

```cpp
// 编辑器子系统（核心 API）
#include "MetaHumanCharacterEditorSubsystem.h"

// 导出函数库
#include "MetaHumanCharacterExportBlueprintLibrary.h"

// 角色构建
#include "Subsystem/MetaHumanCharacterBuild.h"

// 皮肤材质
#include "Subsystem/MetaHumanCharacterSkinMaterials.h"

// 编辑器设置
#include "MetaHumanCharacterEditorSettings.h"

// 几何体移除（服装隐藏面处理）
#include "MetaHumanGeometryRemoval.h"
```

### 基本用法

**注册角色并进行编辑**（来自 `MetaHumanCharacterEditorSubsystem.h`）：

```cpp
// 获取编辑器子系统
UMetaHumanCharacterEditorSubsystem* Subsystem = UMetaHumanCharacterEditorSubsystem::Get();
if (!Subsystem) return;

// 加载一个 MetaHuman 角色资产
UMetaHumanCharacter* Character = LoadObject<UMetaHumanCharacter>(nullptr, TEXT("/Game/MetaHumans/MyCharacter"));

// 注册角色进行编辑
if (Subsystem->TryAddObjectToEdit(Character))
{
    // 角色已注册，可以进行编辑操作
    // ...
    
    // 编辑完成后，取消注册
    // Subsystem->RemoveObjectToEdit(Character);
}
```

**通过蓝图函数库导出 DNA**（来自 `MetaHumanCharacterExportBlueprintLibrary.h`）：

```cpp
#include "MetaHumanCharacterExportBlueprintLibrary.h"

UMetaHumanCharacter* Character = /* 加载或获取角色 */;

FMetaHumanDNAExportParams Params;
Params.ProjectPath = TEXT("/Game/MetaHumans");
Params.ExternalPath = TEXT("D:/Export");
Params.bDNAHead = true;
Params.bDNABody = true;
Params.bOverwriteExistingAssets = true;

UMetaHumanCharacterExportBlueprintLibrary::ExportDNA(Character, Params);
```

### 进阶用法

**构建 MetaHuman 角色**（来自 `Subsystem/MetaHumanCharacterBuild.h`）：

```cpp
#include "Subsystem/MetaHumanCharacterBuild.h"

UMetaHumanCharacter* Character = /* 角色引用 */;

FMetaHumanCharacterEditorBuildParameters BuildParams;
BuildParams.PipelineType = EMetaHumanDefaultPipelineType::Cinematic;
BuildParams.PipelineQuality = EMetaHumanQualityLevel::Cinematic;
BuildParams.AnimationSystemName = TEXT("AnimBP");
BuildParams.AbsoluteBuildPath = TEXT("/Game/MetaHumans/MyCharacter");
BuildParams.bEnableWardrobeItemValidation = true;

// 执行构建
FMetaHumanCharacterEditorBuild::BuildMetaHumanCharacter(Character, BuildParams);
```

**合并头部和身体网格体**（来自 `Subsystem/MetaHumanCharacterBuild.h`）：

```cpp
#include "Subsystem/MetaHumanCharacterBuild.h"

USkeletalMesh* FaceMesh = /* 头部网格 */;
USkeletalMesh* BodyMesh = /* 身体网格 */;

UE::MetaHuman::FMergedMeshMapping MeshMapping;

// 创建持久化资产
USkeletalMesh* MergedMesh = FMetaHumanCharacterEditorBuild::MergeHeadAndBody_CreateAsset(
    FaceMesh,
    BodyMesh,
    TEXT("/Game/MetaHumans/Common/MergedMesh"),
    ELodUpdateOption::All,
    &MeshMapping
);

// 或创建瞬态对象
USkeletalMesh* TransientMergedMesh = FMetaHumanCharacterEditorBuild::MergeHeadAndBody_CreateTransient(
    FaceMesh,
    BodyMesh,
    GetTransientPackage()
);
```

**操作皮肤材质参数**（来自 `Subsystem/MetaHumanCharacterSkinMaterials.h`）：

```cpp
#include "Subsystem/MetaHumanCharacterSkinMaterials.h"

// 获取面部材质槽名称
FName SlotName = FMetaHumanCharacterSkinMaterials::GetSkinMaterialSlotName(EMetaHumanCharacterSkinMaterialSlot::Head);

// 应用皮肤参数到材质
FMetaHumanCharacterFaceMaterialSet FaceMaterialSet;
UMaterialInstanceDynamic* BodyMID = /* 身部材质实例 */;
FMetaHumanCharacterSkinSettings SkinSettings;

FMetaHumanCharacterSkinMaterials::ApplySkinParametersToMaterials(FaceMaterialSet, BodyMID, SkinSettings);

// 应用雀斑参数
FMetaHumanCharacterSkinMaterials::ApplyFrecklesParameterToMaterial(
    FaceMaterialSet,
    EMetaHumanCharacterFrecklesParameter::Density,
    0.5f
);

// 应用肤色区域（Accent）参数
FMetaHumanCharacterSkinMaterials::ApplySkinAccentParameterToMaterial(
    FaceMaterialSet,
    EMetaHumanCharacterAccentRegion::Cheeks,
    EMetaHumanCharacterAccentRegionParameter::Redness,
    0.7f
);
```

## Demo 示例

以下是一个最小可编译的 C++ 示例，展示如何在编辑器工具中操作 MetaHuman 角色。

**MyMetaHumanTool.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCharacterEditorSubsystem.h"
#include "Subsystem/MetaHumanCharacterBuild.h"

class FMyMetaHumanTool
{
public:
    /** 导出角色的 DNA 到项目内容 */
    static bool ExportCharacterDNA(UMetaHumanCharacter* InCharacter, const FString& InOutputPath);

    /** 构建角色为运行时可用的资产 */
    static bool BuildCharacter(UMetaHumanCharacter* InCharacter, const FString& InBuildPath);
};
```

**MyMetaHumanTool.cpp**

```cpp
#include "MyMetaHumanTool.h"
#include "MetaHumanCharacterExportBlueprintLibrary.h"

bool FMyMetaHumanTool::ExportCharacterDNA(UMetaHumanCharacter* InCharacter, const FString& InOutputPath)
{
    if (!InCharacter)
    {
        return false;
    }

    FMetaHumanDNAExportParams Params;
    Params.ProjectPath = InOutputPath;
    Params.bDNAHead = true;
    Params.bDNABody = true;
    Params.bOverwriteExistingAssets = true;

    UMetaHumanCharacterExportBlueprintLibrary::ExportDNA(InCharacter, Params);
    return true;
}

bool FMyMetaHumanTool::BuildCharacter(UMetaHumanCharacter* InCharacter, const FString& InBuildPath)
{
    UMetaHumanCharacterEditorSubsystem* Subsystem = UMetaHumanCharacterEditorSubsystem::Get();
    if (!Subsystem || !InCharacter)
    {
        return false;
    }

    FMetaHumanCharacterEditorBuildParameters BuildParams;
    BuildParams.PipelineType = EMetaHumanDefaultPipelineType::Cinematic;
    BuildParams.PipelineQuality = EMetaHumanQualityLevel::Cinematic;
    BuildParams.AbsoluteBuildPath = InBuildPath;
    BuildParams.bEnableWardrobeItemValidation = true;

    FMetaHumanCharacterEditorBuild::BuildMetaHumanCharacter(InCharacter, BuildParams);
    return true;
}
```

## 模块依赖

由于 MetaHumanCharacterEditor 模块大量依赖 MetaHuman 内部模块和 UE 核心系统，以下是需要关注的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心角色数据资产和身份模型定义 |
| `MetaHumanCharacterPalette` | 角色调色板和服装收集系统 |
| `MetaHumanDefaultPipeline` | 默认角色构建管线 |
| `DNAInterchange` | DNA 文件格式导入导出（通过 Interchange 框架） |
| `MetaHumanRigLogic` | RigLogic 评估和骨骼动画逻辑 |
| `MetaHumanFaceTextureSynthesizer` | 面部纹理合成模型引擎 |
| `GeometryFramework` | 编辑器中的动态网格交互（用于雕刻和操控工具） |
| `ToolWidgets` | 交互式编辑器工具 UI 框架 |

> 注意：该插件还依赖一系列 Epic 内部的 MetaHuman 相关模块（如 MetaHumanIdentity、MetaHumanARService 等），这些模块通常不可在标准 UE 源码之外单独使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `95d906ba` | [UEMHC] Checking for Asset Registry filter validity before using it | 修复资产注册表过滤器使用前的合法性检查 |
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 更新 MetaHuman Titan 引擎至 v9.0.8 |
| 2026-05-26 | `efb27122` | [UEMHC] Duplicate face/body DNA when duplicating archetype skel meshes | 修复复制原型骨骼网格时面部/身体 DNA 未正确复制的问题 |
| 2026-05-26 | `909bc538` | [MHC] Use safer weak pointers for captured objects in MHC preview delegates | 使用更安全的弱指针避免预览委托中的悬空引用 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 更新 MetaHuman Titan 引擎至 v9.0.7 |

### 维护评价

- **创建时间**：2025 年 3 月，约 1 年历史
- **更新频率**：非常活跃，最近一次更新在 2026 年 5 月 26 日，同日有多次提交，表明处于密集开发期
- **维护状态**：**活跃维护中** — 作为 Epic 官方 MetaHuman 生态系统的核心组件，持续有功能更新和 bug 修复
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true`，且 `EnabledByDefault=false`，表明该插件仍处于测试阶段，需要手动启用
- **已知限制**：
  - 依赖 MetaHuman 可选内容安装（通过 `IsOptionalMetaHumanContentInstalled()` 检查）
  - 纹理合成需要本地模型目录（在项目设置中配置）
  - 所有模块标记为 Runtime 类型，但实际包含大量编辑器专用代码
- **推荐使用**：推荐用于正在开发 MetaHuman 工作流的项目，但需注意其 Beta 状态意味着 API 可能在后续版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- 官方文档（.uplugin 中未提供 DocsURL，请参考 [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)）
- 测试用例（该插件的测试文件位于引擎测试目录中，非插件内部目录）