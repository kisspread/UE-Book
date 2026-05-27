# Datasmith FBX Importer

> Adds support for importing content from DeltaGen and VRED into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | Datasmith FBX 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithVREDTranslator` (Editor), `DatasmithDeltaGenTranslator` (Editor), `DatasmithFBXTranslator` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter) | |

## 用途

此插件为 Unreal Engine 提供了从 **DeltaGen** 和 **VRED** 这两款专业工业设计（尤其是汽车设计）3D可视化软件导出的 FBX 文件进行高级导入的能力。标准的 FBX 导入器可能无法完美处理这两款软件生成的复杂场景、材质、动画和特定节点结构。Datasmith FBX Importer 作为一个**翻译层**，其核心作用是解析这些专有的 FBX 文件，提取并转换其中的场景层次结构（Hierarchy）、几何体、材质属性、灯光参数、相机设置以及复杂的动画序列（包括 `AnimBlocks` 和 `AnimClips`），将其映射到 Unreal Engine 的 Datasmith 框架和 Actor 体系中，从而实现高保真度的资产导入。

## 使用场景

- 你在使用 **Autodesk VRED** 创建产品可视化或虚拟评审场景，需要将其复杂的场景结构、材质和动画无损地导入到 Unreal Engine 中进行实时渲染和交互开发。
- 你在使用 **DeltaGen** 进行汽车设计可视化，需要将其模型、材质（包括特殊的三平面投射等）、环境灯光和相机轨迹导入到 UE5 中创建虚拟展厅或配置器。
- 你需要导入包含 **VRED 特有动画系统**（如 `AnimBlocks` 和 `AnimClips`）的 FBX 文件，这些动画控制着多个部件的序列和切换。

## 蓝图用法

此插件主要是一个导入器，其功能通常通过 **编辑器导入操作** 触发，而不是在运行时通过蓝图节点直接调用。其核心交互体现在 **导入选项** 的配置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TextureDirs` | 配置纹理文件的搜索路径，解决 FBX 中纹理引用相对路径的问题。 | `UDatasmithFBXImportOptions` |

### 使用示例（蓝图描述）

1.  在 Content Browser 中右键，选择 **Import**。
2.  选择从 DeltaGen 或 VRED 导出的 `.fbx` 文件。
3.  在弹出的 **FBX Import Options** 对话框中，如果安装了此插件，你将看到额外的 **Datasmith** 选项卡或特定于该插件的选项。
4.  在选项中，你可以配置 **Texture folders** (`TextureDirs`)，添加 FBX 文件中引用的纹理可能存放的目录。
5.  确认导入后，插件将自动处理场景转换，生成对应的 StaticMesh、Material、Actor 等资产。

## C++ 用法

此插件主要在编辑器和工具链层面工作，其 C++ API 通常用于扩展或定制导入流程。

### 头文件引入

```cpp
#include "DatasmithFBXTranslatorModule.h"
#include "DatasmithFBXFileImporter.h"
#include "DatasmithFBXScene.h"
```

### 基本用法

插件的核心是将 FBX 解析为 `FDatasmithFBXScene` 中间表示，然后处理这个场景。
*（概念性代码，实际使用通常由 Datasmith 导入框架内部调用）*

```cpp
// 假设我们已经通过 FBX SDK 获取了 FbxScene* 和相关选项
FbxScene* FbxScene = ...;
const UDatasmithFBXImportOptions* Options = ...;
const FDatasmithImportBaseOptions* BaseOptions = ...;

// 创建 FBX 文件导入器
FDatasmithFBXFileImporter FBXImporter(FbxScene, &MyIntermediateScene, Options, BaseOptions);

// 执行导入，将 FBX 数据解析到 FDatasmithFBXScene 结构中
FBXImporter.ImportScene();

// 此时 MyIntermediateScene 包含了从 FBX 解析出的完整场景数据：
// - RootNode (场景根节点)
// - Materials (所有材质)
// - AnimNodes (动画数据)
// 等等
```

### 进阶用法

在得到中间场景表示 `FDatasmithFBXScene` 后，通常会使用 `FDatasmithFBXSceneProcessor` 进行优化和清理，然后再由具体的 `FDatasmithFBXImporter`（如 VRED 或 DeltaGen 的实现）将其转换为 Datasmith 元素。

```cpp
FDatasmithFBXSceneProcessor SceneProcessor(&MyIntermediateScene);

// 优化场景结构
SceneProcessor.FindDuplicatedMaterials(); // 去除重复材质
SceneProcessor.FindDuplicatedMeshes();    // 去除重复网格
SceneProcessor.RemoveInvisibleNodes();    // 移除不可见节点
SceneProcessor.SimplifyNodeHierarchy();   // 简化节点层次
SceneProcessor.FixNodeNames();            // 修正节点名称
// ... 更多优化步骤 ...

// 然后使用特定的导入器（例如 FDatasmithVREDImporter）转换为 Datasmith 元素
FDatasmithVREDImporter VREDImporter;
VREDImporter.ImportScene(&MyIntermediateScene);
// VREDImporter 内部会生成 IDatasmithScene, IDatasmithMeshElement 等
```

## Demo 示例

以下是一个展示如何创建并使用 `FDatasmithFBXScene` 和 `FDatasmithFBXSceneNode` 来构建一个简单场景结构的最小示例。

### MyFBXSceneDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DatasmithFBXScene.h"

class FMyFBXSceneDemo
{
public:
    void BuildDemoScene();

private:
    FDatasmithFBXScene DemoScene;
};
```

### MyFBXSceneDemo.cpp
```cpp
#include "MyFBXSceneDemo.h"

void FMyFBXSceneDemo::BuildDemoScene()
{
    // 创建一个根节点
    TSharedPtr<FDatasmithFBXSceneNode> RootNode = MakeShared<FDatasmithFBXSceneNode>();
    RootNode->Name = TEXT("SceneRoot");
    RootNode->LocalTransform = FTransform::Identity;
    DemoScene.RootNode = RootNode;

    // 创建一个子节点（代表一个物体）
    TSharedPtr<FDatasmithFBXSceneNode> ChildNode = MakeShared<FDatasmithFBXSceneNode>();
    ChildNode->Name = TEXT("CarBody");
    ChildNode->OriginalName = TEXT("CarBody_Original");
    ChildNode->LocalTransform = FTransform(FRotator(0, 90, 0), FVector(100, 0, 0), FVector(1.0));

    // 为该节点创建一个网格
    TSharedPtr<FDatasmithFBXSceneMesh> Mesh = MakeShared<FDatasmithFBXSceneMesh>();
    Mesh->Name = TEXT("CarBody_Mesh");
    // 注意：实际 MeshDescription 数据需要通过 FBX SDK 或 Mesh Description API 填充，此处省略。
    ChildNode->Mesh = Mesh;

    // 创建一个材质并分配给节点
    TSharedPtr<FDatasmithFBXSceneMaterial> Material = MakeShared<FDatasmithFBXSceneMaterial>();
    Material->Name = TEXT("CarPaint");
    Material->ScalarParams.Add(TEXT("Metallic"), 0.8f);
    Material->ScalarParams.Add(TEXT("Roughness"), 0.2f);
    ChildNode->Materials.Add(Material);
    // 将材质也添加到场景的全局材质列表（如果需要去重）
    DemoScene.Materials.Add(Material);

    // 将子节点添加到根节点
    RootNode->AddChild(ChildNode);

    // 遍历并打印场景结构
    FDatasmithFBXSceneNode::Traverse(DemoScene.RootNode, [](const TSharedPtr<FDatasmithFBXSceneNode>& Node)
    {
        UE_LOG(LogTemp, Log, TEXT("Node: %s, Children: %d"), *Node->Name, Node->Children.Num());
    });
}
```

## 模块依赖

此插件在 `.uplugin` 中声明了对以下插件的依赖，你的项目或模块如果需要使用此插件的功能，通常需要间接依赖这些模块。

| 模块 | 用途 |
|---|---|
| `DatasmithImporter` | Datasmith 核心导入框架，提供 `IDatasmithScene` 等基础接口和导入管理器。 |
| `DatasmithContent` | Datasmith 内容模块，包含 Datasmith 特有的资产类型（如 `UDatasmithAssetImportData`）。 |
| `FBX` / `FBX` (通过 Unreal 的 FBX SDK 集成) | 底层 FBX 文件读写库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点导致的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 迁移到 `UE_LOGF` 以适配新的日志宏。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码错误。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复琐碎的不可达代码警告。 |
| 2024-10-02 | `0a14cf0e` | Update VRED python exporter to support API changes in VRED | 更新 VRED Python 导出器以支持 VRED API 变更。 |

### 维护评价

- **创建时间**：6 年前（2019年），属于较老的插件。
- **活跃度**：从 Git 提交记录看，**最近一次实质性功能更新（VRED 导出器适配）停留在 2024 年 10 月**。2025 年和 2026 年的提交全部是**编译器警告/错误修复和代码维护**（如迁移日志宏、修复浮点精度问题），没有任何新功能或特性更新。
- **状态**：该插件已进入**成熟稳定期**，主要进行兼容性维护。它针对特定工业软件（VRED/DeltaGen）的 FBX 导入，功能基本定型。
- **建议**：对于需要导入 VRED 或 DeltaGen 场景的项目，**可以使用**。但需要知晓，其核心代码库已不活跃，未来可能不会添加对新特性的支持，仅会适配引擎版本变化。如果你的资产来自其他 FBX 工具，应使用标准的 FBX Importer 或 Datasmith Importer。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithFBXImporter)
- 官方文档：暂无
- 测试用例：插件目录内未发现标准测试用例文件，其功能通常通过项目资产导入流程进行验证。