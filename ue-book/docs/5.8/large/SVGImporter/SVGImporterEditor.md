# SVG Importer

> Importing and handling SVG files

| 属性 | 值 |
|---|---|
| 中文名 | SVG 导入器 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、UI 工厂、编辑器工具） |
| 模块 | `SVGImporter` (Runtime), `SVGImporterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter) | |

## 用途

`SVGImporter` 插件的核心功能是在 Unreal Engine 的虚拟制片（Virtual Production）工作流中，导入和解析标准的 SVG（可缩放矢量图形）文件。它解决的核心问题是：如何将设计师在 Adobe Illustrator、Inkscape 等矢量绘图软件中创作的 2D 图形（如 Logo、UI 元素、装饰图案）无缝引入 UE5 的 3D 环境，并转换为可用于渲染、交互或进一步处理的几何数据（`USVGData` 资产和 3D 网格体）。

该插件不仅仅是简单的文件导入，它还包含一套完整的解析管线：从原始的 SVG XML 文本，解析出结构化的元素树（`FSVGRawElement`），再将其转换为更高级、可生成几何体的元素（`FSVGBaseElement` 及其子类，如 `FSVGPath`, `FSVGCircle`）。它支持解析 SVG 的基本形状、路径命令、样式（CSS 类）和渐变，并在 Editor 模块中提供了资产导入工厂、内容浏览器缩略图、编辑器菜单集成和交互式 3D 可视化器。

简而言之，它是连接 2D 矢量设计与 UE5 3D 虚拟世界的桥梁，专为虚拟制片流程中的资产准备工作而设计。

## 使用场景

-   **虚拟制片资产准备**：为虚拟拍摄场景导入高质量的品牌 Logo、片头标题、环境装饰图形等矢量资产，并将其转换为可在 3D 空间中放置和渲染的网格体。
-   **游戏/UI 设计**：将设计稿中的矢量图标、UI 框架等导入引擎，用于创建可缩放、不失真的用户界面元素或游戏内贴花。
-   **参数化形状生成**：在蓝图或 C++ 中，通过提供 SVG 路径字符串或文本缓冲，动态生成几何网格，用于程序化内容生成或特殊效果。

## 蓝图用法

该插件的蓝图接口主要通过 `FSVGImporterEditorUtils` 提供的静态函数暴露，用于以编程方式创建或更新 SVG 数据资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create SVG Data From Text Buffer` | 从一个包含 SVG 文本的字符串中创建一个新的 `USVGData` 资产对象。 | `USVGImporterEditorUtils` |
| `Refresh SVG Data From Text Buffer` | 使用新的 SVG 文本缓冲区更新一个已有的 `USVGData` 资产。 | `USVGImporterEditorUtils` |
| `Get Initializer From SVG Data` | 从 SVG 文本缓冲区创建一个初始化器结构体 (`FSVGDataInitializer`)，可用于稍后初始化或刷新 `USVGData`。 | `USVGImporterEditorUtils` |

### 使用示例（蓝图描述）

1.  **通过字符串创建资产**：
    -   在蓝图中，使用 `Load File to String` 节点读取一个 `.svg` 文件的内容到一个字符串变量 (`SVGText`)。
    -   然后调用 `Create SVG Data From Text Buffer` 节点。将 `SVGText` 连接到 `In SVG Text Buffer` 引脚。
    -   为 `In Outer` 引脚指定一个资产包（如通过 `Project Content` 获取一个目录）。
    -   为 `In Name` 引脚指定资产名称（如 `“MyLogo”`）。
    -   该节点的输出即为创建成功的 `USVGData` 资产对象，可将其保存到磁盘或在后续逻辑中使用。

2.  **更新已有资产**：
    -   通过 `Load Asset` 节点加载一个已存在的 `USVGData` 资产 (`OldSVGData`)。
    -   读取新的 SVG 文件内容到新字符串 (`NewSVGText`)。
    -   调用 `Refresh SVG Data From Text Buffer` 节点，将 `OldSVGData` 和 `NewSVGText` 分别连接到对应引脚。该操作会原地更新资产数据。

## C++ 用法

### 头文件引入

使用编辑器工具函数：
```cpp
#include "SVGImporterEditorUtils.h"
```
使用解析工具：
```cpp
#include "SVGParsingUtils.h"
```
操作原始 SVG 元素：
```cpp
#include "Types/SVGRawElement.h"
#include "Types/SVGRawAttribute.h"
```

### 基本用法

以下代码演示了如何解析一个 SVG 字符串并创建 `USVGData` 资产，这是插件最核心的导入流程。
```cpp
// 文件路径: Engine/Plugins/VirtualProduction/SVGImporter/Source/SVGImporterEditor/Private/SVGImporterEditorUtils.cpp (逻辑推断)
// 假设在某个编辑器工具类中
#include "SVGImporterEditorUtils.h"
#include "SVGParsingUtils.h"

void CreateMySVGAsset()
{
    // 1. 读取或准备一个 SVG 字符串
    FString SVGText = TEXT("<svg width=\"100\" height=\"100\"><circle cx=\"50\" cy=\"50\" r=\"40\" fill=\"red\"/></svg>");

    // 2. 验证字符串是否为有效 SVG
    if (!FSVGParsingUtils::IsValidSVGString(SVGText))
    {
        UE_LOG(LogTemp, Warning, TEXT("Provided string is not a valid SVG."));
        return;
    }

    // 3. 创建一个临时的 Outer 对象（通常是一个 UFactory 或 UTransient 包）
    UObject* Outer = GetTransientPackage(); // 或者是一个自定义的工厂对象

    // 4. 调用核心函数创建 SVGData
    USVGData* NewSVGData = FSVGImporterEditorUtils::CreateSVGDataFromTextBuffer(
        SVGText,
        Outer,
        FName(TEXT("RuntimeGeneratedSVG")),
        RF_Public | RF_Standalone
    );

    if (NewSVGData)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully created SVGData: %s"), *NewSVGData->GetName());
        // 接下来可以将 NewSVGData 保存到磁盘，或用于生成动态网格等
    }
}
```

### 进阶用法

该用法展示了如何手动控制 SVG 解析管线，从最底层的原始元素开始，适用于需要深度定制解析过程或提取特定数据的场景。
```cpp
// 文件路径: Engine/Plugins/VirtualProduction/SVGImporter/Source/SVGImporterEditor/Private/SVGImporterEditorUtils.cpp (逻辑推断)
#include "SVGImporterEditorUtils.h"
#include "SVGParsingUtils.h"
#include "Types/SVGRawElement.h"
#include "Types/SVGRawAttribute.h"

void AdvancedSVGParsing()
{
    FString ComplexSVG = TEXT(R"(
    <svg>
        <style>.highlight { fill: yellow; }</style>
        <g id="group1">
            <rect class="highlight" x="10" y="10" width="80" height="80"/>
            <circle cx="50" cy="50" r="30"/>
        </g>
    </svg>
    )");

    // 1. 选择解析器 (可选择 FastXml 或 PugiXml)
    TSharedRef<FSVGParser_Base> Parser = FSVGParsingUtils::CreateSVGParser(
        ComplexSVG,
        FSVGParsingUtils::ESVGParserType::SVGPugiXml // 推荐使用 PugiXml，功能更完整
    );

    // 2. 执行解析
    if (!Parser->Parse(true))
    {
        UE_LOG(LogTemp, Error, TEXT("SVG Parsing failed!"));
        return;
    }

    // 3. 获取原始元素树根节点
    const TSharedPtr<FSVGRawElement>& Root = Parser->GetRootElement();
    if (!Root)
    {
        UE_LOG(LogTemp, Error, TEXT("Root element is null after parsing."));
        return;
    }

    // 4. 调试输出原始元素信息 (可选)
    Root->PrintDebugInfo();

    // 5. 将原始元素树转换为用于几何生成的专用元素
    FSVGImporterEditorUtils::FSVGParsedElements ParsedElements;
    FSVGImporterEditorUtils::ParseRootRawElement(Root.ToSharedRef(), ParsedElements);

    // 6. 获取处理后的元素列表 (已应用样式和渐变)
    const TArray<TSharedRef<FSVGBaseElement>>& FinalElements = ParsedElements.GetOutElements();
    UE_LOG(LogTemp, Log, TEXT("Parsed %d specialized SVG elements."), FinalElements.Num());

    // 现在 FinalElements 中的每个元素 (如 FSVGGroupElement, FSVGRectangle, FSVGCircle)
    // 都包含了用于生成网格体的完整几何和属性信息。
}
```

## Demo 示例

以下是一个完整的、可编译的 C++ 示例，演示如何在运行时模块中解析 SVG 字符串并创建一个临时的 `USVGData` 对象。

**MySVGProcessor.h**
```cpp
// MySVGProcessor.h
#pragma once

#include "CoreMinimal.h"

class USVGData;

class FMySVGProcessor
{
public:
    static USVGData* ProcessSVGString(const FString& InSVGText);
};
```

**MySVGProcessor.cpp**
```cpp
// MySVGProcessor.cpp
#include "MySVGProcessor.h"
#include "SVGImporterEditorUtils.h"
#include "SVGParsingUtils.h"

USVGData* FMySVGProcessor::ProcessSVGString(const FString& InSVGText)
{
    if (!FSVGParsingUtils::IsValidSVGString(InSVGText))
    {
        return nullptr;
    }

    // 使用 Transient 包作为临时 Outer，避免污染项目资产
    USVGData* TransientSVGData = FSVGImporterEditorUtils::CreateSVGDataFromTextBuffer(
        InSVGText,
        GetTransientPackage(),
        NAME_None,
        RF_Transient
    );

    return TransientSVGData;
}
```

## 模块依赖

要使用 `SVGImporter` 插件的功能，你的项目或模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SVGImporter` | 核心运行时模块，包含 SVG 数据资产（`USVGData`）的定义和运行时处理逻辑。 |
| `SVGImporterEditor` | 编辑器扩展模块，包含资产工厂、自定义面板、可视化工具等。如果你需要在编辑器中使用导入功能，必须依赖此模块。 |
| `GeometryScripting` | 用于将解析后的 SVG 元素转换为 `UDynamicMesh` 的几何体。这是生成最终网格的关键依赖。 |
| `pugixml` | 一个轻量级的 C++ XML 解析库，被 `SVGImporterEditor` 模块的 `FSVGParser_PugiXml` 使用，用于解析 SVG 文件的 XML 结构。 |
| `GeometryMask` | 提供几何蒙版功能，可能用于处理 SVG 中的 `clip-path` 属性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移至新的 UE_LOGF 格式，属于代码现代化重构。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次错误的全局查找替换引入的问题。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了编号为 CL51314860 的变更，可能因为引入了未预期的副作用。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复了因委托获取方式错误导致初始化注册失败的问题。 |

### 维护评价

`SVGImporter` 是一个较新的插件，于 2025 年 9 月创建，并标记为 **Beta** 版本。尽管创建时间不长，但从近期的 git 历史（2026 年 2 月、4 月）可以看出，它仍在被**积极维护**。近期的提交主要集中在**代码质量改进、错误修复和系统兼容性适配**上，这表明 Epic 的开发团队正在持续关注并完善该插件。

由于它隶属于“Virtual Production”分类且由 Epic 官方开发，可以预见它将成为虚拟制片管线中的一个重要工具。目前它被标记为实验性和 Beta，意味着 API 和功能可能在未来版本中发生变化。**推荐在需要处理矢量图形资产的虚拟制片项目中尝试和使用**，但应关注其版本更新日志，以应对可能的破坏性更改。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/SVGImporter)
-   官方文档：暂无
-   测试用例：暂无（在提供的文件结构中未发现独立的测试模块或文件）