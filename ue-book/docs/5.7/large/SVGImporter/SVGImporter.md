# SVGImporter (Runtime 模块)

> 核心运行时模块，负责 SVG 数据资产、Actor 体系、动态网格组件和几何体生成。

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | `SVGImporter` |
| 类型 | Runtime |
| LoadingPhase | Default |
| 公共依赖 | `Core`, `GeometryFramework` |
| 第三方依赖 | Nanosvg |

## 架构概览

SVGImporter Runtime 模块是整个 SVG 导入系统的数据和渲染核心。它定义了：

1. **SVG 数据资产**（`USVGData`）：序列化存储 SVG 文件解析后的形状数据
2. **Actor 体系**：一系列 Actor 类用于在关卡中表示 SVG 图形
3. **网格组件体系**：基于 `UDynamicMeshComponent` 的自定义组件，负责几何体生成
4. **类型系统**：SVG 样式、路径、形状等数据结构
5. **工具函数**：几何运算、颜色解析、Spline 转 Polyline 等

## 类层次结构

### Actor 层次

```
AActor
├── ASVGDynamicMeshesContainerActor  (Abstract)  ── 定义 GetSVGDynamicMeshes() 接口
│   ├── ASVGActor                     ── 主要的 SVG Actor，包含完整 SVG 图形
│   ├── ASVGShapesParentActor         ── Split 操作后的父 Actor，管理子 Shape Actor
│   └── ASVGJoinedShapesActor         ── Join 操作后的合并 Actor
├── ASVGShapeActor                    ── Split 后的单个形状 Actor
└── ASVGBakedActor                    ── Bake 操作后的静态网格 Actor
```

### 组件层次

```
UDynamicMeshComponent
└── USVGBaseDynamicMeshComponent      ── 基类，提供 SVG 网格更新通知
    ├── USVGDynamicMeshComponent      ── 单个 SVG 形状的网格组件
    │   ├── USVGFillComponent         ── 填充区域组件（Private）
    │   └── USVGStrokeComponent       ── 描边区域组件（Private）
    └── UJoinedSVGDynamicMeshComponent ── 合并形状的网格组件
```

### 数据类型层次

```
FSVGBaseElement                       ── 所有 SVG 元素的基类
├── FSVGMainElement                   ── SVG 根元素
├── FSVGStyleElement                  ── CSS 样式元素
├── FSVGClipPath                      ── 裁剪路径
├── FSVGGradientElement               ── 渐变元素
└── FSVGGraphicsElement               ── 可绘制图形元素基类
    ├── FSVGGroupElement              ── 分组元素（<g>）
    └── FSVGPath                      ── 路径元素
        ├── FSVGLine                  ── 直线
        ├── FSVGPolyLine              ── 折线
        │   └── FSVGPolygon           ── 多边形
        ├── FSVGRectangle             ── 矩形
        ├── FSVGCircle                ── 圆形
        └── FSVGEllipse               ── 椭圆
```

## 核心类详解

### USVGData

SVG 数据资产，是导入流程的核心产物。存储解析后的 SVG 形状数据，可被多个 SVG Actor 引用。

```cpp
UCLASS()
class SVGIMPORTER_API USVGData : public UObject
```

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `SVGTexture` | `UTexture2D*` | 从 SVG 光栅化生成的纹理 |
| `SVGFileContent` | `FString` | SVG 原始文本内容 |
| `Shapes` | `TArray<FSVGShape>` | 解析后的形状数据 |
| `OverrideQuality` | `ESVGSplineConversionQuality` | Spline 转 Polyline 质量 |

**关键方法（Editor）：**

| 方法 | 说明 |
|---|---|
| `Initialize(FSVGDataInitializer)` | 使用初始化器设置 SVG 数据 |
| `CreateShapes(TArray<FSVGBaseElement>)` | 从解析的元素创建形状 |
| `GenerateSVGTexture()` | 生成 SVG 纹理 |
| `Reimport()` | 重新导入 |

### ASVGActor

关卡中的 SVG 图形 Actor，是用户在编辑器中最常交互的对象。

```cpp
UCLASS()
class SVGIMPORTER_API ASVGActor : public ASVGDynamicMeshesContainerActor
```

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `SVGData` | `USVGData*` | 引用的 SVG 数据资产 |
| `RenderMode` | `ESVGRenderMode` | 渲染模式：3D（DynamicMesh）或 2D（Texture） |
| `Scale` | `float` | 形状缩放 |
| `ExtrudeType` | `ESVGExtrudeType` | 挤出类型：None / FrontFaceOnly / FrontBackMirror |
| `FillsExtrude` | `float` | 填充区域挤出深度 |
| `StrokesExtrude` | `float` | 描边区域挤出深度 |
| `BevelDistance` | `float` | 斜角距离 |
| `StrokesWidth` | `float` | 描边宽度 |
| `StrokeJoinStyle` | `EPolygonOffsetJoinType` | 描边连接样式：Square / Round / Miter |
| `bSmoothFillShapes` | `bool` | 是否平滑填充形状边缘 |
| `bIgnoreStrokes` | `bool` | 是否忽略描边 |
| `bSVGIsUnlit` | `bool` | 是否不受光照影响 |
| `bSVGCastsShadow` | `bool` | 是否投射阴影 |

**关键方法（Editor）：**

| 方法 | 说明 |
|---|---|
| `BakeToBlueprint()` | 将 SVG Actor 烘焙为 Blueprint（StaticMesh） |
| `ResetGeometry()` | 从 SVGData 重新生成几何体 |
| `Split()` | 将 SVG Actor 拆分为多个单形状 Actor |

### USVGDynamicMeshComponent

单个 SVG 形状的动态网格组件。

```cpp
UCLASS(MinimalAPI, ClassGroup=(SVG))
class USVGDynamicMeshComponent : public USVGBaseDynamicMeshComponent
```

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `Color` | `FColor` | 形状颜色 |
| `ExtrudeType` | `ESVGExtrudeType` | 挤出类型 |
| `Extrude` | `float` | 挤出深度 |
| `Bevel` | `float` | 斜角值 |

**关键方法：**

| 方法 | 说明 |
|---|---|
| `FlattenShape()` | 展平为 2D 多边形 |
| `ScaleShape(float)` | 缩放形状 |
| `SetColor(FColor)` | 设置颜色（BlueprintCallable） |
| `BakeStaticMesh()` | 烘焙为 StaticMesh（Editor） |
| `ResetToSVGValues()` | 重置为 SVG 原始值（Editor） |

### UJoinedSVGDynamicMeshComponent

合并多个 SVG 形状后的网格组件，支持单色和分色两种着色模式。

| 属性 | 类型 | 说明 |
|---|---|---|
| `Coloring` | `EJoinedSVGMeshColoring` | 着色模式：SeparateColors / SingleColor |
| `MainColor` | `FLinearColor` | 单色模式的主颜色 |
| `ShapeParametersList` | `TSet<FSVGShapeParameters>` | 分色模式的形状参数 |
| `bSVGIsUnlit` | `bool` | 是否不受光照影响 |

### USVGEngineSubsystem

引擎子系统，提供全局委托用于 SVG Actor 事件通知。

```cpp
UCLASS()
class USVGEngineSubsystem : public UEngineSubsystem
```

**委托：**

| 委托 | 说明 |
|---|---|
| `FSVGActorComponentsReady` | SVG Actor 组件就绪时触发 |
| `FOnSVGActorSplit` | SVG Actor 拆分完成时触发 |
| `FOnSVGShapesUpdated` | SVG 形状更新完成时触发 |

## 关键类型

### FSVGShape

序列化形状数据，存储在 `USVGData::Shapes` 中。

| 成员 | 说明 |
|---|---|
| `Style` (`FSVGStyle`) | 样式（颜色、描边、可见性） |
| `Polygons` (`TArray<FSVGPathPolygon>`) | 多边形列表 |
| `FillGradient` / `StrokeGradient` | 填充/描边渐变 |
| `bIsClosed` | 路径是否闭合 |
| `bIsClockwise` | 多边形方向 |

### FSVGStyle

SVG 样式，类似 Material 的概念。

| 方法 | 说明 |
|---|---|
| `HasStroke()` / `HasFill()` | 是否有描边/填充 |
| `GetFillColor()` / `GetStrokeColor()` | 获取颜色 |
| `GetStrokeWidth()` | 获取描边宽度 |
| `IsVisible()` | 是否可见 |

### FSVGPath

SVG 路径元素，支持所有 SVG 路径指令：

| 指令 | 方法 |
|---|---|
| MoveTo | `MoveTo()` / `PathMoveTo()` |
| LineTo | `LineTo()` / `PathLineTo()` |
| CubicBezierTo | `CubicBezierTo()` / `PathCubicBezierTo()` |
| ClosePath | 通过 `SetIsClosed()` 标记 |

### ESVGRenderMode

```cpp
enum class ESVGRenderMode : uint8
{
    DynamicMesh3D = 0,  // 3D 动态网格
    Texture2D = 1       // 2D 纹理
};
```

### ESVGExtrudeType

```cpp
enum class ESVGExtrudeType : uint8
{
    None,              // 无挤出（平面）
    FrontFaceOnly,     // 仅正面挤出
    FrontBackMirror    // 前后镜像挤出
};
```

## 工具函数（FSVGImporterUtils）

| 方法 | 说明 |
|---|---|
| `ConvertSVGSplineToPolyLine()` | 将 SVG Spline 转换为 Polyline |
| `ShouldPolygonBeDrawn()` | 判断多边形是否应被绘制（fill-rule non-zero） |
| `RotateAroundCustomPivot()` | 围绕自定义轴心旋转点 |
| `GetColorFromSVGString()` | 从 SVG 颜色字符串提取颜色 |
| `StylesFromCSS()` | 从 CSS 字符串提取样式 |
| `SetSVGMatrixFromTransformString()` | 从 SVG transform 字符串设置矩阵 |
| `GetAverageColor()` | 计算颜色平均值 |
| `CreateSVGTexture()` | 从 SVG 文本创建纹理（Editor） |
| `BakeSVGActorToBlueprint()` | 烘焙为 Blueprint（Editor） |
| `SplitSVGActor()` | 拆分 SVG Actor（Editor） |
| `ConsolidateSVGActor()` | 合并 SVG Actor 形状（Editor） |
| `JoinSVGDynamicMeshOwners()` | 合并多个 SVG Actor（Editor） |

## 几何生成流程

1. **导入阶段**（Editor）：`USVGFactory` 读取 .svg 文件 → `FSVGParser_Base` 解析 XML → `FSVGImporterEditorUtils` 将 RawElement 转换为 SVGBaseElement 层次结构 → `USVGData::Initialize()` 创建 `FSVGShape` 数组
2. **实例化阶段**：拖放 USVGData 到关卡 → `USVGActorFactory` 生成 `ASVGActor` → `ASVGActor::Initialize()` → `Generate()`
3. **网格生成**：遍历 `Shapes` → `CreateMeshesFromShape()` → 创建 `USVGFillComponent` / `USVGStrokeComponent` → 使用 Geometry Scripting 生成 DynamicMesh
4. **后处理**：应用挤出、斜角、平滑、缩放、居中

## 源码文件列表

### Public

| 文件 | 说明 |
|---|---|
| `SVGDefines.h` | SVG 常量定义（颜色名、属性名等） |
| `SVGTypes.h` | 序列化类型（FSVGStyle, FSVGShape, FSVGPathPolygon, FSVGGradient） |
| `SVGElements.h` | SVG 元素层次结构（FSVGBaseElement ~ FSVGGroupElement） |
| `SVGPath.h` | SVG 路径和子路径 |
| `SVGGraphicalElements.h` | 图形元素（Line, Circle, Rectangle 等） |
| `SVGData.h` | USVGData 资产类 |
| `SVGActor.h` | ASVGActor 主 Actor |
| `SVGDynamicMeshesContainerActor.h` | 抽象基类 |
| `SVGShapesParentActor.h` | Split 后的父 Actor |
| `SVGBakedActor.h` | 烘焙后的 Actor |
| `SVGEngineSubsystem.h` | 引擎子系统 |
| `SVGImporterUtils.h` | 工具函数 |
| `SVGImporter.h` | 模块头文件 |
| `SVGActorEditorComponent.h` | 编辑器辅助组件 |
| `ProceduralMeshes/SVGBaseDynamicMeshComponent.h` | 基础网格组件 |
| `ProceduralMeshes/SVGDynamicMeshComponent.h` | SVG 形状网格组件 |
| `ProceduralMeshes/JoinedSVGDynamicMeshComponent.h` | 合并形状网格组件 |

### Private

| 文件 | 说明 |
|---|---|
| `SVGImporterSettings.h` | 插件设置 |
| `SVGShapeActor.h` | 单形状 Actor |
| `SVGJoinedShapesActor.h` | 合并形状 Actor |
| `ProceduralMeshes/SVGFillComponent.h` | 填充区域组件 |
| `ProceduralMeshes/SVGStrokeComponent.h` | 描边区域组件 |
