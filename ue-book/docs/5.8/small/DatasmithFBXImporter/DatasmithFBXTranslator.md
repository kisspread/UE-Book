```markdown
# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithFBXTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithVREDTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏩 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

本插件是 Datasmith 导入管线的专用 FBX 翻译层，专门用于将工业级可视化软件 **DeltaGen**（PTC）和 **VRED**（Autodesk）导出的 FBX 文件转换为 Unreal Engine 可消费的 Datasmith 场景元素。

与标准 FBX 导入器不同，本插件额外处理了这两个工业软件的特殊数据：
- **VRED 特有功能**：动画块（AnimBlock）/ 动画剪辑（AnimClip）系统、Switch/Toggle 材质变体、场景切换（Scene Switch）和 Transform 变体、场景合并（Scene Merge）
- **DeltaGen 特有功能**：通过 `.tml` 辅助文件导入动画数据、特殊的单位缩放因子（0.1）
- **共享功能**：VRED 风格的三角平面投影（Triplanar）材质、灯光朝向修正（VRED 灯光朝 -Z，UE 朝 +X）、相机朝向修正、场景层级优化与简化

本质上，它将 FBX 中的几何体、材质、灯光、相机、动画数据解析为中间表示（`FDatasmithFBXScene`），经过场景处理优化后，再转换为 Datasmith 元素供引擎使用。

**默认未启用**：需要在 Edit → Plugins 中手动启用，或通过 `.uproject` 配置文件开启。

## 使用场景

- 你使用 **VRED** 制作汽车/产品可视化场景，需要将带有完整动画、材质变体、场景切换的 FBX 导入 UE → 用 VRED 翻译器
- 你使用 **DeltaGen** 进行汽车行业实时渲染预览，需要将 FBX + TML 动画数据导入 UE → 用 DeltaGen 翻译器
- 你需要在 UE 中保留 VRED 的 Switch/Toggle 物体状态和动画剪辑系统 → 本插件是唯一途径
- 你需要在 Datasmith 导入流程中自动优化场景层级、去除重复材质/网格、修复命名 → 依赖 `FDatasmithFBXSceneProcessor`

## 蓝图用法

本插件为纯 C++ Editor 模块，不暴露蓝图可调用的节点。所有导入功能通过 Datasmith 导入对话框触发（File → Import Into Level → 选择 FBX 文件）。

导入选项通过以下类配置（出现在导入对话框面板中）：

### 核心类

| 类 | 说明 |
|---|---|
| `UDatasmithFBXImportOptions` | FBX 导入配置选项，可设置纹理搜索目录 |
| `FDatasmithFBXScene` | FBX 场景的中间表示，包含完整的节点层级、材质、网格、动画数据 |
| `FDatasmithFBXSceneNode` | 场景节点，描述层级结构、变换、关联的网格/材质/灯光/相机 |
| `FDatasmithFBXSceneMaterial` | 材质描述，支持向量/标量/布尔/纹理参数，含 UV 投影和平面投影 |
| `FDatasmithFBXSceneMesh` | 网格描述，基于 `FMeshDescription` 存储几何数据 |

### 使用示例（编辑器操作）

1. 启用插件：Edit → Plugins → 搜索 "Datasmith FBX Importer" → Enable
2. 导入：File → Import Into Level → 选择 DeltaGen 或 VRED 导出的 `.fbx` 文件
3. 在导入选项面板中设置纹理搜索目录（Texture folders）
4. 点击 Import 完成导入

## C++ 用法

本插件的 C++ API 主要用于扩展或自定义 FBX 导入流程。以下代码展示核心数据结构的使用方式。

### 头文件引入

```cpp
#include "DatasmithFBXScene.h"
#include "DatasmithFBXImporter.h"
#include "DatasmithFBXFileImporter.h"
#include "DatasmithFBXSceneProcessor.h"
#include "DatasmithFBXImportOptions.h"
```

### 基本用法 — 遍历 FBX 场景节点

```cpp
// 基于 Public/DatasmithFBXScene.h 中 FDatasmithFBXSceneNode::Traverse 的设计模式
// 获取场景所有节点并遍历
TArray<TSharedPtr<FDatasmithFBXSceneNode>> AllNodes = FBXScene->GetAllNodes();

for (auto& Node : AllNodes)
{
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("Node: %s, Children: %d"),
        *Node->Name, Node->Children.Num());

    // 检查节点关联的网格
    if (Node->Mesh.IsValid())
    {
        UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Mesh: %s, MaterialCount: %d"),
            *Node->Mesh->Name, Node->ImportMaterialCount);
    }

    // 检查节点关联的灯光
    if (Node->Light.IsValid())
    {
        UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Light: %s, Type: %d, Intensity: %.2f"),
            *Node->Light->Name,
            (int32)Node->Light->LightType,
            Node->Light->Intensity);
    }
}
```

### 基本用法 — 获取场景统计信息

```cpp
// 基于 Public/DatasmithFBXScene.h 中 FDatasmithFBXScene::GetStats
FDatasmithFBXScene::FStats Stats = FBXScene->GetStats();

UE_LOG(LogDatasmithFBXImport, Log, 
    TEXT("Scene Stats - Materials: %d, Meshes: %d, Geometry: %d, Nodes: %d"),
    Stats.MaterialCount, Stats.MeshCount, 
    Stats.GeometryCount, Stats.NodeCount);
```

### 进阶用法 — 场景优化处理

```cpp
// 基于 Public/DatasmithFBXSceneProcessor.h 中的方法调用顺序
// FDatasmithFBXSceneProcessor 负责在导入后优化中间场景

FDatasmithFBXSceneProcessor Processor(FBXScene.Get());

// 1. 合并重复材质（相同属性的材质合并为一个）
Processor.FindDuplicatedMaterials();

// 2. 合并重复网格（相同几何数据的网格合并为一个）
Processor.FindDuplicatedMeshes();

// 3. 移除辅助节点
Processor.RemoveLightMapNodes();   // 移除光照贴图辅助节点
Processor.RemoveInvisibleNodes();  // 移除不可见节点
Processor.RemoveEmptyNodes();      // 移除空节点
Processor.RemoveTempNodes();       // 移除 VRED 导出时产生的临时几何体

// 4. 标记需要保持的节点（Switch/Toggle 等变体节点）
Processor.FindPersistentNodes();

// 5. 修正命名问题
Processor.FixNodeNames();          // 修正节点名中的空白字符
Processor.FixMeshNames();          // 修正不能用作资产名的网格名（如 'AUX', 'CON'）

// 6. 拆分灯光和相机节点（修正朝向差异）
Processor.SplitLightNodes();       // VRED 灯光朝 -Z，UE 灯光朝 +X
Processor.SplitCameraNodes();      // 同理，相机也需要拆分

// 7. 简化层级
Processor.SimplifyNodeHierarchy();
```

### 进阶用法 — 材质纹理参数

```cpp
// 基于 Public/DatasmithFBXScene.h 中 FDatasmithFBXSceneMaterial::FTextureParams
// VRED/DeltaGen 的材质支持多种纹理投影方式

for (auto& [ParamName, TextureParam] : Material->TextureParams)
{
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("Texture: %s"), *ParamName);
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Path: %s"), *TextureParam.Path);
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Projection: %d"), (int32)TextureParam.ProjectionType);

    // 纹理投影类型
    switch (TextureParam.ProjectionType)
    {
    case ETextureMapType::UV:
        // 标准 UV 映射
        break;
    case ETextureMapType::Planar:
        // 平面投影 — 使用 Translation/Rotation/Scale 控制
        UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Planar Translation: %s"),
            *TextureParam.Translation.ToString());
        break;
    case ETextureMapType::Triplanar:
        // 三角平面投影 — VRED 特有
        UE_LOG(LogDatasmithFBXImport, Log, TEXT("  Triplanar BlendBias: %.2f"),
            TextureParam.TriplanarBlendBias);
        break;
    }
}
```

## Demo 示例

以下展示如何在 C++ 中程序化创建一个 FBX 场景节点并查询其内容：

```cpp
// FBXSceneDemo.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithFBXScene.h"

class FFBXSceneDemo
{
public:
    static void LogSceneInfo(const TSharedRef<FDatasmithFBXScene>& Scene);
    static int32 CountNodesByType(const TSharedRef<FDatasmithFBXSceneNode>& Root, ENodeType Type);
};
```

```cpp
// FBXSceneDemo.cpp
#include "FBXSceneDemo.h"

void FFBXSceneDemo::LogSceneInfo(const TSharedRef<FDatasmithFBXScene>& Scene)
{
    // 输出基础场景信息
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("ScaleFactor: %.2f, BaseTime: %.1f, PlaybackSpeed: %.1f"),
        Scene->ScaleFactor, Scene->BaseTime, Scene->PlaybackSpeed);

    // 输出场景统计
    FDatasmithFBXScene::FStats Stats = Scene->GetStats();
    UE_LOG(LogDatasmithFBXImport, Log, 
        TEXT("Materials: %d, Meshes: %d, Geometry: %d, Nodes: %d"),
        Stats.MaterialCount, Stats.MeshCount, Stats.GeometryCount, Stats.NodeCount);

    // 输出动画信息
    UE_LOG(LogDatasmithFBXImport, Log, TEXT("AnimNodes: %d, SwitchObjects: %d, ToggleObjects: %d"),
        Scene->AnimNodes.Num(), Scene->SwitchObjects.Num(), Scene->ToggleObjects.Num());

    // 使用静态遍历模板遍历所有节点
    if (Scene->RootNode.IsValid())
    {
        int32 NodeCount = 0;
        FDatasmithFBXSceneNode::Traverse(Scene->RootNode, [&NodeCount](TSharedPtr<FDatasmithFBXSceneNode> Node)
        {
            NodeCount++;
        });
        UE_LOG(LogDatasmithFBXImport, Log, TEXT("Total traversed nodes: %d"), NodeCount);
    }
}

int32 FFBXSceneDemo::CountNodesByType(const TSharedRef<FDatasmithFBXSceneNode>& Root, ENodeType Type)
{
    int32 Count = 0;
    FDatasmithFBXSceneNode::Traverse(Root, [&Count, Type](TSharedPtr<FDatasmithFBXSceneNode> Node)
    {
        if (EnumHasAnyFlags(Node->GetNodeType(), Type))
        {
            Count++;
        }
    });
    return Count;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 核心导入框架 |
| `DatasmithContent` | Datasmith 内容类型定义 |
| `DatasmithCore` | Datasmith 核心接口和类型 |

模块自身依赖（从 Build.cs 推断）：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 网格几何数据处理 |
| `FBX` / `FBXStaticMeshLibrary` | Autodesk FBX SDK 封装，用于解析 FBX 文件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复简单的不可达代码警告 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出脚本以适配 VRED API 变更 |

### 维护评价

本插件创建于 2019 年，已有约 **7 年**历史。最近的更新全部为编译警告修复和日志宏迁移，属于被动维护性质，没有功能性更新。2024 年有过一次 VRED 导出脚本的适配更新。

- **维护频率**：低，每年仅 1-2 次提交
- **更新类型**：主要是编译兼容性修复，无新功能
- **默认启用**：❌ 否，说明 Epic 将其定位为按需使用的专用工具
- **实验性**：否，已标记为正式版
- **适用人群**：仅限使用 DeltaGen 或 VRED 的工业可视化用户

⚠️ **提示**：该插件功能稳定但更新频率很低。如果你的 VRED/DeltaGen 版本较新，可能需要关注 FBX 格式兼容性。对于标准 FBX 文件的导入，应使用 UE 内置的 FBX Importer。

**推荐使用**：✅ 在 DeltaGen/VRED 工作流中推荐使用；标准用户无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [Datasmith 官方文档](https://docs.unrealengine.com/en-US/datasmith/)
```