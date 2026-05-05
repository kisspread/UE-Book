# SVGImporterEditor (Editor 模块)

> 编辑器模块，负责 SVG 文件导入、XML 解析、编辑器 UI 集成和资产操作。

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | `SVGImporterEditor` |
| 类型 | Editor |
| LoadingPhase | Default |
| 公共依赖 | `Core` |
| 第三方依赖 | Nanosvg, pugixml |

## 架构概览

SVGImporterEditor 模块是 SVG 导入系统的编辑器层，负责：

1. **文件导入**：UFactory 实现，支持拖放 .svg 文件到 Content Browser
2. **XML 解析**：两种解析器后端（FastXml 和 PugiXml）
3. **SVG 元素转换**：将原始 XML 元素转换为结构化的 SVGBaseElement 层次
4. **编辑器 UI**：属性面板自定义、右键菜单、缩略图渲染、可视化器
5. **Actor 工厂**：支持从 USVGData 资产生成 ASVGActor

## 导入流程

```
.svg 文件
    │
    ▼
USVGFactory::FactoryCreateText()        ── 检测 .svg 扩展名
    │
    ▼
FSVGParser_FastXml / FSVGParser_PugiXml ── XML 解析，生成 FSVGRawElement 层次
    │
    ▼
FSVGImporterEditorUtils::ParseRootRawElement()  ── 转换为 FSVGBaseElement 层次
    │                                              应用 CSS 样式、渐变
    ▼
USVGData::Initialize()                  ── 创建 FSVGShape 数组
    │
    ▼
USVGData::GenerateSVGTexture()          ── nanosvg 光栅化生成纹理
    │
    ▼
USVGData::CreateShapes()                ── 生成最终形状数据
```

## 核心类详解

### USVGFactory

SVG 文件导入工厂，注册 .svg 文件扩展名。

```cpp
UCLASS()
class USVGFactory : public UFactory
```

- `FactoryCanImport()`：检查文件扩展名是否为 .svg
- `FactoryCreateText()`：处理文本格式的 SVG 文件导入
- `FactoryCreateNew()`：创建新的 USVGData 资产

### USVGReimportFactory

支持重新导入（Reimport）功能的工厂，当源 SVG 文件更新时可以刷新资产。

### USVGActorFactory

Actor 工厂，支持从 Content Browser 拖放 USVGData 资产到关卡时自动创建 ASVGActor。

```cpp
UCLASS(MinimalAPI)
class USVGActorFactory : public UActorFactory
```

### FSVGParser_Base

SVG XML 解析器基类。

```cpp
class FSVGParser_Base : public TSharedFromThis<FSVGParser_Base>
```

- `Parse()`：解析 SVG 文本，返回是否成功
- `IsValidSVG()`：验证文本是否为有效 SVG
- `GetRootElement()`：获取解析后的根元素层次

### FSVGParser_FastXml

基于 UE 内置 FastXml 的解析器实现。

### FSVGParser_PugiXml

基于 pugixml 的解析器实现，提供更完整的 XML 解析能力。

### FSVGImporterEditorUtils

编辑器工具类，负责将原始 XML 元素转换为结构化 SVG 元素。

```cpp
class FSVGImporterEditorUtils
```

**关键方法：**

| 方法 | 说明 |
|---|---|
| `CreateSVGDataFromTextBuffer()` | 从 SVG 文本创建 USVGData 资产 |
| `RefreshSVGDataFromTextBuffer()` | 刷新已有 USVGData |
| `GetInitializerFromSVGData()` | 创建 FSVGDataInitializer |
| `ParseRootRawElement()` | 解析根元素层次为 SVGBaseElement |

**内部类 FSVGParsedElements：**

管理解析过程中收集的元素、样式和渐变信息，在解析完成后统一应用样式（`ApplyStyles()`）和渐变（`ApplyGradients()`）。

**支持的 SVG 元素：**

| 元素 | 创建方法 |
|---|---|
| `<svg>` | `CreateSVG()` |
| `<g>` | `CreateGroup()` |
| `<style>` | `CreateStyle()` |
| `<clipPath>` | `CreateClipPath()` |
| `<linearGradient>` / `<radialGradient>` | `CreateGradient()` |
| `<circle>` | `CreateCircle()` |
| `<ellipse>` | `CreateEllipse()` |
| `<rect>` | `CreateRectangle()` |
| `<line>` | `CreateLine()` |
| `<polyline>` | `CreatePolyLine()` |
| `<polygon>` | `CreatePolygon()` |
| `<path>` | `CreatePath()` |

### FSVGRawElement / FSVGRawItem / FSVGRawAttribute

原始 XML 解析结果的数据结构：

- `FSVGRawElement`：XML 元素（标签、属性、子元素）
- `FSVGRawItem`：XML 节点基类
- `FSVGRawAttribute`：XML 属性（键值对）

### FSVGImporterEditorModule

编辑器模块主类，负责模块启动/关闭和菜单注册。

```cpp
class FSVGImporterEditorModule : public ISVGImporterEditorModule
```

**功能：**

- 注册 SVG 资产类型
- 注册右键菜单扩展（SVG Actor 操作）
- 支持从剪贴板粘贴 SVG 内容创建 Actor
- 注册编辑器命令（`FSVGImporterEditorCommands`）

### ISVGImporterEditorModule

模块接口，提供：

- `GetStyleName()`：获取编辑器样式名
- `GetSVGImporterMenuCategoryName()`：获取菜单分类名
- `AddSVGActorMenuEntries()`：添加 SVG Actor 右键菜单项

## 编辑器集成

### 属性面板自定义

| 类 | 说明 |
|---|---|
| `FSVGShapeParametersDetails` | FSVGShapeParameters 的属性自定义 |
| `FSVGCategoryTypeCustomization` | SVG 分类类型自定义 |
| `FJoinedSVGDynamicMeshComponentCustomization` | 合并网格组件的属性自定义 |

### 可视化器

| 类 | 说明 |
|---|---|
| `FSVGDynamicMeshVisualizer` | SVG 动态网格可视化器 |
| `FSVGActorEditorComponentVisualizer` | SVG Actor 编辑器组件可视化器 |

### 右键菜单（SVGActorContextMenu）

为 ASVGActor 提供上下文菜单操作：
- Split（拆分）
- Consolidate（合并形状）
- Join（合并多个 Actor）
- Bake to Blueprint（烘焙）

### 缩略图渲染

`FSVGThumbnailRenderer`：为 USVGData 资产生成缩略图预览。

### 资产定义

`UAssetDefinition_SVGData`：定义 USVGData 资产在 Content Browser 中的行为（双击、右键菜单等）。

### 编辑器样式

`FSVGImporterEditorStyle`：注册编辑器图标和样式集。

## 源码文件列表

### Public

| 文件 | 说明 |
|---|---|
| `ISVGImporterEditorModule.h` | 模块接口 |
| `SVGImporterEditorCommands.h` | 编辑器命令定义 |
| `Factories/SVGActorFactory.h` | Actor 工厂 |

### Private

| 文件 | 说明 |
|---|---|
| `SVGImporterEditorModule.h` | 模块实现 |
| `SVGImporterEditorStyle.h` | 编辑器样式 |
| `SVGImporterEditorUtils.h` | 编辑器工具函数（核心转换逻辑） |
| `SVGParser_Base.h` | 解析器基类 |
| `SVGParser_FastXml.h` | FastXml 解析器 |
| `SVGParser_PugiXml.h` | PugiXml 解析器 |
| `SVGParsingUtils.h` | 解析工具函数 |
| `SVGThumbnailRenderer.h` | 缩略图渲染器 |
| `SVGDynamicMeshVisualizer.h` | 网格可视化器 |
| `SVGActorEditorComponentVisualizer.h` | Actor 编辑器组件可视化器 |
| `SVGActorContextMenu.h` | 右键菜单 |
| `AssetDefinition_SVGData.h` | 资产类型定义 |
| `Factories/SVGFactory.h` | SVG 导入工厂 |
| `Factories/SVGReimportFactory.h` | 重新导入工厂 |
| `Types/SVGRawElement.h` | 原始 XML 元素 |
| `Types/SVGRawItem.h` | 原始 XML 节点 |
| `Types/SVGRawAttribute.h` | 原始 XML 属性 |
| `Customizations/SVGShapeParametersDetails.h` | 形状参数属性自定义 |
| `Customizations/SVGCategoryTypeCustomization.h` | 分类类型自定义 |
| `Customizations/JoinedSVGDynamicMeshComponentCustomization.h` | 合并组件自定义 |

## 依赖关系

SVGImporterEditor 依赖 SVGImporter（Runtime 模块），形成典型的 Editor-over-Runtime 模式：

```
SVGImporterEditor (Editor)
    ├── SVGImporter (Runtime)  ── 核心数据类型和 Actor
    ├── UnrealEd               ── 编辑器框架
    ├── AssetTools              ── 资产管理
    ├── pugixml                 ── XML 解析
    ├── ToolMenus               ── 菜单扩展
    └── PropertyEditor          ── 属性自定义
```
