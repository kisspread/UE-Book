# SVG Importer

> Importing and handling SVG files

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、默认网格资源） |
| 模块 | `SVGImporter` (Runtime), `SVGImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SVGImporter) | |

## 用途

SVGImporter 是一个 UE5 编辑器插件，用于将 SVG（Scalable Vector Graphics）矢量图文件导入引擎并转换为 3D 动态网格（DynamicMesh）或 2D 纹理。它解决了在虚拟制片和 Motion Design 工作流中将矢量设计资产直接引入 Unreal Engine 的问题——传统上只能导入位图，而矢量图的无损缩放和可编辑性使其成为 UI 图标、品牌标识、舞台背景等场景的理想选择。

插件使用 [nanosvg](https://github.com/memononen/nanosvg) 作为 SVG 解析/光栅化后端，使用 [pugixml](https://pugixml.org/) 作为 XML 解析后端，将 SVG 元素（path、rect、circle、ellipse、line、polygon、polyline）解析为结构化数据，再通过 Geometry Scripting 和 Geometry Framework 生成 DynamicMesh 3D 几何体。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [SVGImporter](SVGImporter.md) | Runtime | 核心运行时模块：SVG 数据资产、Actor、网格组件、几何生成 |
| [SVGImporterEditor](SVGImporterEditor.md) | Editor | 编辑器模块：SVG 文件导入工厂、解析器、编辑器 UI、右键菜单 |

## 使用场景

- 你在做虚拟制片的舞台设计 → 导入品牌 Logo 的 SVG 文件，自动转为 3D 网格并调整挤出深度
- 你需要在 Motion Design 中使用矢量图标 → 拖入 SVG 文件到关卡，直接生成带颜色和样式的 3D 形状
- 你想把 2D 矢量设计快速转为 3D 模型 → 使用 SVG Importer 的挤出（Extrude）和斜角（Bevel）功能
- 你需要从 SVG 生成 2D 纹理 → 切换到 Texture2D 渲染模式，利用 nanosvg 光栅化
- 你想把 SVG 图形烘焙为 StaticMesh Blueprint → 使用 BakeToBlueprint 功能

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetScale` | 设置 SVG 形状的缩放 | `ASVGActor` |
| `SetFillsExtrude` | 设置填充区域的挤出深度 | `ASVGActor` |
| `SetStrokesExtrude` | 设置描边区域的挤出深度 | `ASVGActor` |
| `SetBevelDistance` | 设置斜角距离 | `ASVGActor` |
| `SetStrokesWidth` | 设置描边宽度 | `ASVGActor` |
| `SetShapesOffset` | 设置形状间距偏移 | `ASVGActor` |
| `SetVisible` | 显示/隐藏 SVG Actor | `ASVGActor` |
| `SetColor` | 设置 SVG 形状组件颜色 | `USVGDynamicMeshComponent` |
| `FlattenShape` | 将 SVG 形状展平为 2D 多边形 | `USVGDynamicMeshComponent` |
| `ScaleShape` | 缩放 SVG 形状 | `USVGDynamicMeshComponent` |

### 使用示例（蓝图描述）

1. 在 Content Browser 中拖入 .svg 文件 → 自动生成 USVGData 资产
2. 将 USVGData 资产拖入关卡 → 自动生成 ASVGActor
3. 在 ASVGActor 的 Details 面板中调整 `RenderMode`（3D/2D）、`ExtrudeType`、`Scale` 等参数
4. 右键 ASVGActor → SVG 菜单 → Split（拆分为多个 Actor）/ Consolidate（合并形状）/ Join（合并多个 Actor）

## C++ 用法

### 头文件引入

```cpp
#include "SVGData.h"
#include "SVGActor.h"
#include "SVGImporterUtils.h"
#include "SVGDynamicMeshComponent.h"
```

### 基本用法

```cpp
// 从 SVG 文本创建 SVGData 资产（编辑器环境）
FString SVGText = TEXT("<svg>...</svg>");
FSVGDataInitializer Initializer(SVGText, TEXT("MyDesign.svg"));
USVGData* SVGData = NewObject<USVGData>(GetTransientPackage(), TEXT("MySVGData"));
SVGData->Initialize(Initializer);

// 在关卡中生成 SVG Actor
ASVGActor* SVGActor = World->SpawnActor<ASVGActor>();
SVGActor->SVGData = SVGData;
SVGActor->Initialize();
```

### 进阶用法

```cpp
// 使用 FSVGImporterUtils 拆分 SVG Actor 为多个独立 Actor
ASVGShapesParentActor* ParentActor = FSVGImporterUtils::SplitSVGActor(SVGActor);

// 合并多个 SVG Actor 的形状为单个 JoinedShapes Actor
TArray<ASVGDynamicMeshesContainerActor*> Actors = {Actor1, Actor2};
ASVGJoinedShapesActor* JoinedActor = FSVGImporterUtils::JoinSVGDynamicMeshOwners(Actors);

// 将 SVG Actor 烘焙为 Blueprint（生成 StaticMesh + Material）
FSVGImporterUtils::BakeSVGActorToBlueprint(SVGActor, TEXT("/Game/SVGBaked"));

// 从 SVG 字符串创建纹理
UTexture2D* Texture = FSVGImporterUtils::CreateSVGTexture(SVGText, GetTransientPackage());
```

## Demo 示例

### 最小 C++ 模块依赖（Build.cs）

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "SVGImporter"   // Runtime 模块
});

// 如果需要在编辑器中导入 SVG 文件
if (Target.Type == TargetRules.TargetType.Editor)
{
    PrivateDependencyModuleNames.Add("SVGImporterEditor");
}
```

### 读取 SVGData 并查询形状

```cpp
// 读取已有的 SVGData 资产
USVGData* SVGData = LoadObject<USVGData>(nullptr, TEXT("/Game/MySVGAsset"));

// 遍历所有形状
for (const FSVGShape& Shape : SVGData->Shapes)
{
    FColor FillColor = Shape.GetFillColor();
    FColor StrokeColor = Shape.GetStrokeColor();
    bool bClosed = Shape.IsClosed();

    for (const FSVGPathPolygon& Polygon : Shape.GetPolygons())
    {
        const TArray<FVector>& Vertices = Polygon.GetVertices();
        // ... 使用顶点数据
    }
}
```

## 模块依赖

### SVGImporter (Runtime) 依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `GeometryFramework` | DynamicMeshComponent 基础设施 |
| `GeometryCore` | 几何数据结构（Polygon2 等） |
| `GeometryAlgorithms` | 几何算法 |
| `GeometryScriptingCore` | 几何脚本 API |
| `DeveloperSettings` | 插件设置基础设施 |
| `Slate` / `SlateCore` | UI 框架 |
| `Nanosvg` | SVG 解析和光栅化（第三方） |

### SVGImporterEditor (Editor) 依赖

| 模块 | 用途 |
|---|---|
| `SVGImporter` | 运行时核心模块 |
| `UnrealEd` | 编辑器框架 |
| `AssetTools` | 资产导入/管理 |
| `AssetDefinition` | 资产类型定义 |
| `ContentBrowser` | 内容浏览器集成 |
| `pugixml` | XML 解析（第三方） |
| `XmlParser` | XML 解析辅助 |
| `ToolMenus` | 编辑器菜单扩展 |
| `PropertyEditor` / `DetailCustomizations` | 属性面板自定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-04 | `a18b5e45423a` | 从 Experimental 迁移到 VirtualProduction，标记为 Beta |
| 2025-05-08 | `91a8c1f04f45` | 添加 SVG 组件可见性切换，材质从 Translucent 改为 Masked 避免法线反转 |
| 2025-04-07 | `c985b7b81c2e` | 改用独立安装的 pugixml |

插件最初于 2024-01-30 在 Experimental 目录下创建，经过约 1 年半的开发后迁移到 VirtualProduction 分类。近期更新集中在渲染改进（材质类型、可见性控制）和依赖管理（pugixml 独立化）。

### 维护评价

- **状态**: ⚠️ 实验性/Beta（`IsBetaVersion=true`）
- **年龄**: 约 2 年（2024 年 1 月创建于 Experimental，2025 年 9 月迁移到 VirtualProduction）
- **活跃度**: 2025 年有多次功能性更新（材质改进、可见性控制、pugixml 迁移、目录迁移），处于活跃开发中
- **已知限制**:
  - 标记为 Beta，API 可能在后续版本中发生变化
  - SVG 规范支持不完整（如 fill-rule 仅支持 non-zero，渐变的 spreadMethod/gradientTransform 尚未实现）
  - 部分代码有 todo 标记（如 SVGHelperLibrary 可能移到 Editor 模块）
- **推荐**: 适用于 Motion Design 和虚拟制片工作流的早期实验，生产环境需谨慎评估

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/SVGImporter)
- 官方文档（无）
