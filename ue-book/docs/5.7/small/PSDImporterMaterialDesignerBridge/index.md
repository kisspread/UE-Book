# PSD Importer Material Designer Bridge

> 

| 属性 | 值 |
|---|---|
| 中文名 | PSD材质桥接 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码和PSD文档资源） |
| 模块 | `PSDImporterMaterialDesignerBridge` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge) | |

---

## 用途

PSD Importer Material Designer Bridge 是 **PSD 导入器**和 **Dynamic Material（Material Designer）** 之间的桥梁插件。  
当使用内置的 PSD 导入器将 `.psd` 文件导入为 `UPSDDocument` 资源后，本插件可以：

- **自动生成 Material Designer 材质**：将 PSD 的图层、混合模式、裁剪信息转换为 Material Designer 中的材质层（Layer），并保留每个图层的独立纹理（发光、透明度等）。
- **创建四边形 Actor（Quad Actor）**：将 PSD 图层的层级关系生成多个 `APSDQuadActor` / `APSDQuadMeshActor`，用于在场景中以 3D 四边形展示 PSD 内容，每个四边形对应一个图层，并应用对应的 Material Designer 材质。
- **集成到内容浏览器**：右键 PSD 文档资源，直接一键创建 Material Designer 材质或 Quad Actor，无需手动搭建节点。

该插件旨在让 2D PSD 资源能够无缝进入 **Material Designer（Dynamic Material）** 的材质编辑流程，适合需要高级材质效果（如动态混合、裁剪、UV 调整）的 2D 资产管线。

---

## 使用场景

- **UI 或 2D 游戏素材**：将 PSD 中的图层结构自动转化为 Material Designer 材质，实现运行时动态调整图层属性（如发光强度、透明度、裁剪区域）。
- **材质设计原型**：设计师修改 PSD 文件后，只需重新导入并执行“生成材质”命令，即可更新材质效果，无需手动重建材质图。
- **混合材质测试**：利用 Material Designer 的节点图，在 PSD 图层基础上叠加自定义着色器效果（如噪声、扭曲）。

---

## 蓝图用法

本插件当前**未暴露**任何 BlueprintCallable 函数或 BlueprintReadWrite 属性。所有操作均通过编辑器菜单或 C++ 代码完成。

### 编辑器操作

在内容浏览器中选中一个 `PSDDocument` 资源（由 PSD 导入器创建的资产），右键菜单会新增两个选项：

- **Create Material Designer Material**：直接生成一个 `UDynamicMaterialInstance` 资源。
- **Create PSD Quads (Instance)**：在活动世界中创建一组 `APSDQuadActor`，每个图层对应一个 `APSDQuadMeshActor`，并应用实例化的材质（Instance）。
- **Create PSD Quads (Copy)**：类似 Instance，但每个 Quad 使用材质的独立拷贝（Copy）。

这些操作由 `PSDImporterMaterialDesignerContentBrowserIntegration` 类中的菜单扩展实现，源码位于 `PSDImporterMDContentBrowserIntegration.h`。

---

## C++ 用法

### 头文件引入

```cpp
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDDocument.h" // PSD 导入器提供的文档类
```

### 基本用法

#### 1. 从 PSD 文档创建 Material Designer 材质

```cpp
// 假设已有有效的 UPSDDocument* InDocument（通过 PSD 导入器获得）
UPSDImporterMDMaterialFactory* Factory = NewObject<UPSDImporterMDMaterialFactory>();
if (Factory->CanCreateMaterial(InDocument))
{
    UDynamicMaterialInstance* Material = Factory->CreateMaterial(InDocument);
    // Material 现在包含与 PSD 图层结构对应的材质层
}
```

**来源**：`PSDImporterMDMaterialFactory.h` / `.cpp`

#### 2. 创建 PSD Quad Actors（在世界中生成四边网格）

```cpp
// 假设有 UWorld* World 和 UPSDDocument* Document
UPSDImporterMDQuadsFactory* QuadFactory = NewObject<UPSDImporterMDQuadsFactory>();
APSDQuadActor* QuadActor = QuadFactory->CreateQuadActor(*World, *Document);

// 生成图层对应的 quad mesh，选择实例化或拷贝模式
QuadFactory->CreateQuads(*QuadActor, EPSDImporterMaterialDesignerType::Instance);
```

**来源**：`PSDImporterMDQuadsFactory.h` / `.cpp`

---

## Demo 示例

以下是一个最小 C++ 示例，演示如何从 PSD 文档生成 Material Designer 材质并创建 Quad Actors。假设在编辑器模块中的某个命令执行函数。

```cpp
// MyPSDBridgeCommand.cpp
#include "Factories/PSDImporterMDMaterialFactory.h"
#include "Factories/PSDImporterMDQuadsFactory.h"
#include "PSDDocument.h"
#include "Engine/World.h"

void ExecutePSDBridge(UPSDDocument* PSDDoc, UWorld* World)
{
    if (!PSDDoc || !World)
        return;

    // 1. 创建材质
    UPSDImporterMDMaterialFactory* MatFactory = NewObject<UPSDImporterMDMaterialFactory>();
    if (MatFactory->CanCreateMaterial(PSDDoc))
    {
        UDynamicMaterialInstance* MatInst = MatFactory->CreateMaterial(PSDDoc);
        // 可以根据需要将 MatInst 保存为资产
    }

    // 2. 创建四边形 actors
    UPSDImporterMDQuadsFactory* QuadFactory = NewObject<UPSDImporterMDQuadsFactory>();
    APSDQuadActor* QuadActor = QuadFactory->CreateQuadActor(*World, *PSDDoc);
    if (QuadActor)
    {
        // 以实例模式生成所有图层对应的网格
        QuadFactory->CreateQuads(*QuadActor, EPSDImporterMaterialDesignerType::Instance);
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | Material Designer（材质设计器）运行时和编辑器模块，提供 `UDynamicMaterialInstance`、`UDMMaterialLayerObject` 等关键类型 |
| `PSDImporter` | PSD 导入器模块，提供 `UPSDDocument` 和 `FPSDFileLayer` 等数据结构 |
| `PSDImporterMaterialDesignerBridge` | 本插件本身（无需额外依赖） |

**无特殊依赖**（除以上两个非标准依赖外，其余均为标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

- 2025-04-28 `fed4030e` — PSD Importer: Renamed and moved to Experimental （将插件从原本位置重命名并移到 Experimental 目录）
- 2025-04-28 `9216b924` — Horde issue 881859 （Horde 构建系统问题修复，可能与插件创建有关）

### 维护评价

- **创建时间**：2025-04-28，距今不足一个月（极新）。
- **最近更新**：仅有两个提交，均为创建或迁移时的基础提交，无后续功能/修复更新。
- **维护状态**：处于**实验性**阶段（`.uplugin` 中 `IsExperimentalVersion=true`），功能可能不稳定或接口可能变更。
- **已知问题**：未发现已知问题列表，但由于是新插件，可能缺少边界测试。
- **建议**：适合在尝鲜或搭建原型时使用，生产环境请谨慎评估并做好相关测试。如果项目需要稳定版本，可等待后续迭代或考虑手动实现类似功能。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporterMaterialDesignerBridge)
- [PSD 导入器官方文档](https://docs.unrealengine.com/5.0/en-US/PSDImporter/)（插件本身无独立文档，PSD 导入器文档提供基础背景）
- [Dynamic Material 官方文档](https://docs.unrealengine.com/5.0/en-US/DynamicMaterial/)