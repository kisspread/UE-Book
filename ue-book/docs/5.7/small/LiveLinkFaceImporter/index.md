# LiveLinkFaceImporter

> Imports CSV recordings from the Live Link Face app.

| 属性 | 值 |
|---|---|
| 中文名 | 面部CSV导入器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkFaceImporter` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-05-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkFaceImporter) | |

## 用途

该插件提供了一种在 UE 编辑器中将 **Live Link Face** iOS 应用录制并导出的 CSV 文件直接导入为 LiveLink 面部动画数据的方式。  
开发者可以将 iPhone 上离线记录的混合形状（Blend Shape）数值导入引擎，生成可复用的动画资产（例如 `AnimSequence` 或 `LiveLinkFrameData`），从而避免实时串流时的网络限制，便于对录制数据进行后期编辑和重用。

## 使用场景

- 你在制作面部动画，没有实时串流条件，希望使用 iPhone 录制好的 CSV 数据。
- 团队需要将面部表演数据归档，再批量导入到项目中进行剪辑和重定向。
- 需要离线测试不同版本的动画数据，而不依赖 iPhone 的实时连接。
- 项目使用 LiveLink 作为面部动画管线，需要将外部录制数据注入 pipeline。

## 蓝图用法

该插件内部实现为一个 **UFactory** 子类，不暴露任何可调用的蓝图节点。  
所有导入操作均通过 **内容浏览器（Content Browser）** 完成：

1. 确保插件已启用（Project Settings → Plugins → LiveLinkFaceImporter → Enable）。
2. 在内容浏览器中右键任意文件夹，选择 **Import to / ...**。
3. 文件类型筛选器中将出现 `.csv` 文件（来自 Live Link Face app 的录制输出）。
4. 选择 CSV 文件后，编辑器会自动解析并创建对应的面部动画资产（通常为 `AnimSequence` 或 `LiveLinkAnimFrameData`）。

> 无需手动调用任何蓝图函数。

## C++ 用法

该组件主要为编辑器提供导入功能，没有暴露给游戏运行时使用的 C++ 公共 API。  
如需在 C++ 中手动调用导入逻辑，可以继承或实例化 `ULiveLinkFaceImporterFactory` 并调用其方法，但官方不推荐绕过标准导入流程。

### 头文件引入

```cpp
#include "LiveLinkFaceImporterFactory.h"
```

### 基本用法

以下代码片段演示如何在自定义导入器中使用工厂的 CSV 解析逻辑（从测试用例 / 插件实现中提取）：

```cpp
// 构建文件内容字符串
FString CSVContent;
FFileHelper::LoadFileToString(CSVContent, *CSVFilePath);

// 创建工厂实例（临时使用）
ULiveLinkFaceImporterFactory* Factory = NewObject<ULiveLinkFaceImporterFactory>();

// 解析 CSV 行与键
TArray<FString> KeyArray, LineArray;
FString LogMessage;
if (Factory->LoadCSV(CSVContent, KeyArray, LineArray, LogMessage))
{
    // 成功解析，可根据 KeyArray 和 LineArray 构建 LiveLink 数据
    // ...
}
```

> 来源: `Engine/Plugins/Experimental/LiveLinkFaceImporter/Source/LiveLinkFaceImporter/Private/LiveLinkFaceImporterFactory.cpp` (未提供完整源码，上述为核心流程示意)

### 进阶用法

插件设计为纯编辑器工具，不提供复杂的 C++ 集成接口。  
如果你需要从 C++ 对导出数据做后处理，建议先通过标准导入获得资产，再使用 LiveLink API 操作。

## Demo 示例

由于该插件不提供运行时模块，没有可直接运行的 Gameplay 示例。  
以下是一个最小化自定义工具类的框架，用于展示如何在 C++ 中调用 CSV 解析：

**MyCSVImporter.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "LiveLinkFaceImporterFactory.h"

class FMyCSVImporter
{
public:
    static bool ImportLiveLinkFaceCSV(const FString& FilePath, TArray<FName>& OutBoneNames, TArray<float>& OutBlendValues);
};
```

**MyCSVImporter.cpp**
```cpp
#include "MyCSVImporter.h"
#include "LiveLinkFaceImporterFactory.h"

bool FMyCSVImporter::ImportLiveLinkFaceCSV(const FString& FilePath, TArray<FName>& OutBoneNames, TArray<float>& OutBlendValues)
{
    FString CSVContent;
    if (!FFileHelper::LoadFileToString(CSVContent, *FilePath))
        return false;

    ULiveLinkFaceImporterFactory* Factory = NewObject<ULiveLinkFaceImporterFactory>();
    TArray<FString> Keys, Lines;
    FString Log;
    if (!Factory->LoadCSV(CSVContent, Keys, Lines, Log))
        return false;

    // 解析第一行（通常为混合形状名称）
    for (const FString& Key : Keys)
    {
        OutBoneNames.Add(FName(*Key));
    }

    // 解析第一帧数据（假设 Lines 每行对应一帧）
    if (Lines.Num() > 0)
    {
        TArray<FString> Values;
        Lines[0].ParseIntoArray(Values, TEXT(","), true);
        for (const FString& Val : Values)
        {
            OutBlendValues.Add(FCString::Atof(*Val));
        }
    }

    return true;
}
```

> 注意：上述代码仅为演示，实际 CSV 格式取决于 Live Link Face 的导出结构（通常包含时间戳、混合形状名称及数值），请以官方录制数据为准。

## 模块依赖

要使用该插件，你的模块（通常是 Editor 模块）需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|------|------|
| `LiveLink` | 提供 LiveLink 核心数据结构与主题系统，用于构建导入后的面部动画资产 |

其他常见依赖（Core, CoreUObject, Engine, UnrealEd）已在引擎中默认引用，此处省略。

## 维护状态

### 近期更新

- 2024-06-27 `a890c0ce` Fixed some deprecated FString usage.（修复弃用的 FString 用法）
- 2023-08-05 `99b2b2c0` Add 30FPS support to LiveLinkFaceImporter and remove platform restriction（添加 30FPS 支持，移除平台限制）
- 2023-07-27 `912b34bd` Undo //UE5/Release-5.3/... changelist 26640196（撤销一次变更）
- 2023-07-27 `e07a86f7` Add 30FPS support to LiveLinkFaceImporter and remove platform restrictions（添加 30FPS 支持，移除平台限制）
- 2023-05-26 `b6ee3a6c` Fix UE_LOG callsites that have format string-related UB（修复格式字符串相关的未定义行为）

### 维护评价

- **创建时间**：2023 年 5 月，目前约 2 年。
- **最近更新**：2024 年 6 月有一次编译修复，上次功能性更新在 2023 年 8 月。
- **活跃度**：功能性开发已停止超过 12 个月，当前处于维护状态（仅修复兼容性问题）。
- **已知限制**：作为 Beta 插件，可能存在稳定性或格式兼容性问题；推荐在非生产环境使用。
- **是否推荐**：如果你需要导入 Live Link Face 的 CSV 录制数据，这是官方唯一方式，值得启用。但注意它仍是实验性插件，未来可能变更。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LiveLinkFaceImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-face/) (Live Link Face 应用的使用说明)
- 无独立测试用例（插件功能通过编辑器手动测试）