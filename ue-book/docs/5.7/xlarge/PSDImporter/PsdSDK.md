# PSD Importer

> (Description is empty in .uplugin)

| 属性 | 值 |
|---|---|
| 中文名 | PSD导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具和运行时库） |
| 模块 | `PSDImporterEditor` (Editor), `PSDImporter` (Runtime), `PSDImporterCore` (Runtime), `PsdSDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/PSDImporter) | |

## 用途

PSD Importer 是一个实验性编辑器插件，允许用户在 Unreal Editor 中直接导入 Adobe Photoshop (.psd) 文件，并将 PSD 中的图层、蒙版、混合模式等结构转换为引擎内可用的资源（如纹理、材质实例或几何体）。它利用第三方 `PsdSDK` 库（来自 Molecular Matters）来解析 PSD 文件的二进制格式，支持 8、16 和 32 位色深，以及 RGB 和灰度色彩模式。

该插件解决的核心问题是：传统工作流中用户需要手动将 PSD 分层导出为独立图片再导入引擎，流程繁琐且丢失图层组织信息。PSD Importer 实现了单文件导入，保留图层结构、透明度、混合模式等元数据，并能根据图层结构自动生成材质或蓝图资产。

## 使用场景

- **UI/2D 设计师**：将 PSD 界面设计文件直接导入引擎，图层自动生成对应的纹理和材质。
- **角色/道具美术**：从 PSD 中提取分层纹理（如主体、高光、法线贴图通道）。
- **关卡布局预览**：导入带有图层的环境概念图，在引擎中按图层拆分并排列为平面网格。
- **需要保留 PSD 混合模式**：例如使用“正片叠底”、“滤色”等效果的层叠素材。

## 蓝图用法

由于 `PsdSDK` 为纯 C++ 底层库（无 UObject 或 UFUNCTION 暴露），且插件核心逻辑在 C++ 编辑器模块中实现，**蓝图无法直接调用 PSD 导入功能**。编辑器导入操作通过右键菜单或 Content Browser 中的“导入”按钮完成。用户可在编辑器设置中配置导入行为（如是否自动生成纹理、合并图层等），但这些设置项也仅在 C++ 侧定义。

因此，本插件对蓝图开发者是**透明的**——开发者只需像导入普通图片一样操作，引擎会自动处理 PSD 解析与资源生成。

### 核心资源（生成后可在蓝图中使用）

- **UTexture2D**：每个图层或合并结果对应一张纹理。
- **UMaterialInstance**：如果启用了“生成材质”，图层混合模式会被转换为材质节点。
- **UBlueprint**：如果启用了“生成蓝图 Actor”，图层位置信息会转换为 3D 平面。

（具体生成的资产类型取决于编辑器设置，目前未提供公开的 UFUNCTION 用于脚本化导入。）

## C++ 用法

插件以 `PsdSDK` 模块作为底层依赖，直接使用该类库解析 PSD 文件。开发者若需扩展导入逻辑，可引用 `PSDImporterCore` 或 `PSDImporter` 模块的公共接口。

### 头文件引入

```cpp
#include "PSDImporter/Public/PSDImporter.h"   // 假设主工具类
// 或底层 SDK
#include "PsdSDK/Includes/PsdFile.h"
#include "PsdSDK/Includes/PsdNativeFile.h"
```

### 基本用法（使用 PsdSDK 直接读取 PSD 文件）

以下示例来自 `PsdSDK` 头文件中的 API 设计，展示了如何打开、解析并获取图层信息：

```cpp
#include "PsdSDK/Includes/Psd.h"
#include "PsdSDK/Includes/PsdNativeFile.h"
#include "PsdSDK/Includes/PsdMallocAllocator.h"
#include "PsdSDK/Includes/PsdDocument.h"
#include "PsdSDK/Includes/PsdLayer.h"
#include "PsdSDK/Includes/PsdParseDocument.h"  // 假设解析函数

using namespace psd;

void LoadPSDExample(const wchar_t* FilePath)
{
    // 1. 创建分配器和文件对象
    MallocAllocator allocator;
    NativeFile file(&allocator);
    if (!file.OpenRead(FilePath))
        return;

    // 2. 解析文档（ParseDocument 函数从 SDK 提供的示例中推断）
    Document doc;
    if (!ParseDocument(&file, &allocator, &doc))
        return;

    // 3. 访问基本信息
    unsigned int width = doc.width;
    unsigned int height = doc.height;
    unsigned int channelCount = doc.channelCount; // 通常为 3 (RGB) 或 4 (RGBA)
    unsigned int bitsPerChannel = doc.bitsPerChannel;

    // 4. 遍历图层（LayerMaskInfoSection）
    const LayerMaskSection& layerMask = doc.layerMaskInfoSection;
    for (unsigned int i = 0; i < layerMask.layerCount; ++i)
    {
        const Layer& layer = layerMask.layers[i];
        // 图层名称（截断至 31 字符）
        const char* layerName = layer.name.c_str();
        // 图层矩形
        int left = layer.left, top = layer.top, right = layer.right, bottom = layer.bottom;
        // 图层可见性
        bool visible = layer.isVisible;
        // 混合模式键（可通过 blendMode::KeyToEnum 转换）
        uint32_t blendKey = layer.blendModeKey;

        // 通道数据（需手动读取）
        // ...
    }

    // 5. 关闭文件
    file.Close();
}
```

> 注意：上述解析函数 `ParseDocument` 并非 SDK 实际公开的 API 名称，仅为示意。实际 SDK 中解析各 Section 有独立的函数（如 `ParseFileHeader`, `ParseColorModeData`, `ParseImageResources`, `ParseLayerAndMaskInfo`, `ParseImageData`）。具体接口需参考 `PsdParse*.h` 头文件（未在本次文档中提供）。

### 进阶用法（导出 PSD 文件）

SDK 也支持创建并写入 PSD 文件（`PsdExport.h`）：

```cpp
#include "PsdSDK/Includes/PsdExport.h"

psd::ExportDocument* CreateExportExample(psd::Allocator* allocator, unsigned int w, unsigned int h)
{
    psd::ExportDocument* doc = psd::CreateExportDocument(allocator, w, h, 8, psd::exportColorMode::RGB);

    // 添加图层
    unsigned int layerIdx = psd::AddLayer(doc, allocator, "Background");
    // 写入 8-bit 平面数据（R,G,B 分别提供）
    unsigned char* rData = new unsigned char[w * h](); // 示例数据
    unsigned char* gData = new unsigned char[w * h]();
    unsigned char* bData = new unsigned char[w * h]();
    psd::UpdateLayer(doc, allocator, layerIdx, psd::exportChannel::RED,   0, 0, w, h, rData, psd::compressionType::RAW);
    psd::UpdateLayer(doc, allocator, layerIdx, psd::exportChannel::GREEN, 0, 0, w, h, gData, psd::compressionType::RAW);
    psd::UpdateLayer(doc, allocator, layerIdx, psd::exportChannel::BLUE,  0, 0, w, h, bData, psd::compressionType::RAW);

    // 写入文件（需调用 WritePSD 函数，未在此列出）
    // ...

    return doc;
}
```

### 使用插件提供的接口（PSDImporterCore）

`PSDImporterCore` 模块封装了 SDK，提供 UE 风格的数据结构（如 `FPSDImportData`）和纹理生成逻辑。具体接口可在 `Source/PSDImporterCore/Public/` 中找到（本文档不包含）。

## Demo 示例

由于本插件主要面向编辑器操作，不提供独立编译示例。以下是一个最小 C++ 控制台程序（使用 SDK 的独立版）来演示 PSD 解析，但该代码需要 SDK 库文件。

```cpp
// PSDParseDemo.cpp
#include <iostream>
#include "Psd/Psd.h"
#include "Psd/PsdNativeFile.h"
#include "Psd/PsdMallocAllocator.h"
#include "Psd/PsdDocument.h"

int main()
{
    psd::MallocAllocator allocator;
    psd::NativeFile file(&allocator);

    if (!file.OpenRead(L"sample.psd"))
    {
        std::cerr << "Failed to open PSD file." << std::endl;
        return 1;
    }

    // 此处应调用解析函数，但需包含实际解析头文件
    std::cout << "File size: " << file.GetSize() << " bytes." << std::endl;

    file.Close();
    return 0;
}
```

> 注意：以上代码仅为概念验证，实际 `PsdSDK` 的解析函数需要额外引入。完整的示例可参考 SDK 自带的 `samples` 目录（未包含在此文档）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryMask` | 必要依赖，提供几何体蒙版相关功能（具体整合方式未公开） |
| `PsdSDK`（ThirdParty） | 底层 PSD 解析与写入库 |
| `PSDImporterCore` | 封装 SDK，提供 UE 风格的数据结构和纹理生成 |
| `PSDImporter` | 运行时模块，可能包含供蓝图使用的数据资产 |
| `PSDImporterEditor` | 编辑器模块，实现导入 UI、Asset 工厂和设置 |

**省略常见依赖**（Core、CoreUObject、Engine、Slate 等不再列出）。

## 维护状态

### 近期更新

```
- 2025-07-15 bafe5da2 — Silence incorrect V1051 warnings（静默 PVS-Studio 误报）
- 2025-06-05 00f9a7c0 — Add Windows Arm64 libraries for PSD SDK + add build helper batch file（新增 ARM64 库和构建脚本）
- 2025-05-15 41b521d3 — PSD Importer: Importing 16 and 32-bit PSDs now works correctly.（修复 16/32 位 PSD 导入错误）
- 2025-05-15 708e8190 — PSD Importer: Hidden Quad Actor property AdjustForViewDistance because it is not user friendly.（隐藏用户不友好的 Quad Actor 属性）
- 2025-05-15 c35a5c0e — PSD Importer: Importing layers with special characters now sanitzes the layer name.（清理图层名称中的特殊字符）
```

### 维护评价

- **创建时间**：2025-05-15，距今不到 1 年。
- **最近更新**：2025-07-15 有静默警告的修复，2025-06-05 有平台支持扩展，表明近期仍有活跃维护。
- **功能状态**：实验性版本（`IsExperimentalVersion=true`），但已支持 16/32 位 PSD 和图层名清理等基础功能。
- **已知问题**：未提供具体已知问题清单，但作为实验性插件可能存在稳定性或兼容性问题。
- **推荐使用**：适用于需要直接导入 PSD 的 2D/UI 工作流。由于是实验性插件，建议在非生产项目中先行测试。

综合评价：**活跃维护**，推荐有条件地使用。

## 相关链接

- [源码（Plugin 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter)
- [PsdSDK 第三方库（外部）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Source/ThirdParty/PsdSDK)
- [官方文档](https://docs.unrealengine.com/5.7/...)（当前无专用文档页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PSDImporter/Tests)（如有，实际路径可能未公开）