# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types

| 属性 | 值 |
|---|---|
| 中文名 | DMX GDTF 标准库 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

DMXGDTF 插件实现了 [GDTF（General Device Type Format）](https://gdtf-share.com/) 标准在 Unreal Engine 中的完整解析和表示。GDTF 是灯光行业用于描述 DMX 灯具设备类型的开放标准，其 `.gdtf` 文件本质上是一个 **ZIP 压缩包**，内部包含 XML 格式的设备描述文件和相关资源（如 3D 模型）。

该插件解决以下问题：

- **标准化灯具描述**：将 GDTF 标准的 XML 结构映射为 Unreal Engine 原生类型（`UObject`、`USTRUCT` 等），使虚拟制作中可以精确描述灯具的 DMX 通道、属性、几何结构和运动范围
- **GDTF 文件解码**：通过内置的 `DMXZip` 模块解析 `.gdtf` 的 ZIP 容器格式，提取内部 XML 和资源文件
- **从旧版迁移**：取代了之前 `UDMXImportGDTF` 中耦合的 GDTF 实现，将 GDTF 标准独立为可复用的通用插件

**注意**：此插件标记为 `Hidden: true`，不在插件浏览器中显示，作为 DMX 插件生态的内部依赖存在。

## 使用场景

- 你在虚拟制作中需要导入 GDTF 格式的灯具描述文件 → 使用此插件解析 `.gdtf` 文件
- 你需要在运行时读取 GDTF 灯具的 DMX 通道定义和属性映射 → 通过 `DMXGDTF` 模块获取结构化数据
- 你需要处理 ZIP 格式的二进制数据 → 使用 `DMXZip` 模块的 `FDMXZipper` 工具类
- 你正在开发与 DMX 灯具控制相关的工具 → 此插件是底层依赖

## 蓝图用法

`DMXZip` 模块的 `FDMXZipper` 是纯 C++ 工具类，不暴露蓝图节点。如需在蓝图中使用 GDTF 功能，应通过上层 DMX 插件模块间接访问。

## C++ 用法

### 头文件引入

```cpp
#include "DMXZipper.h"
```

### 基本用法 — 加载和读取 ZIP 文件

```cpp
// 引入头文件
#include "DMXZipper.h"

// 创建 Zipper 实例
TSharedRef<FDMXZipper> Zipper = MakeShared<FDMXZipper>();

// 从文件加载（如 .gdtf 文件）
bool bSuccess = Zipper->LoadFromFile(TEXT("/Path/To/MyFixture.gdtf"));

if (bSuccess)
{
    // 获取 ZIP 内所有文件列表
    TArray<FString> Files = Zipper->GetFiles();
    for (const FString& File : Files)
    {
        UE_LOG(LogTemp, Log, TEXT("Found file: %s"), *File);
    }

    // 读取指定文件的内容
    TArray64<uint8> FileData;
    if (Zipper->GetFileContent(TEXT("description.xml"), FileData))
    {
        // 将字节数据转为字符串进行解析
        FString XmlContent;
        FFileHelper::BufferToString(XmlContent, FileData.GetData(), FileData.Num());
    }
}
```

> 来源：`Public/DMXZipper.h`

### 基本用法 — 从内存数据加载

```cpp
// 假设已有从网络或其他来源获取的 GDTF 二进制数据
TArray64<uint8> RawGDTFData = /* ... */;

TSharedRef<FDMXZipper> Zipper = MakeShared<FDMXZipper>();

// 从内存数据加载
bool bSuccess = Zipper->LoadFromData(RawGDTFData);

if (bSuccess)
{
    TArray64<uint8> XmlData;
    if (Zipper->GetFileContent(TEXT("description.xml"), XmlData))
    {
        // 解析 XML 内容
    }
}
```

### 进阶用法 — 创建 ZIP 并保存

```cpp
TSharedRef<FDMXZipper> Zipper = MakeShared<FDMXZipper>();

// 添加文件到 ZIP（相对路径）
TArray64<uint8> XmlContent;
// ... 填充 XmlContent ...
Zipper->AddFile(TEXT("description.xml"), XmlContent, true);  // 压缩存储

// 添加 3D 模型资源
TArray64<uint8> ModelData;
// ... 填充 ModelData ...
Zipper->AddFile(TEXT("models/fixture.3ds"), ModelData, false);  // 不压缩

// 保存到文件
Zipper->SaveToFile(TEXT("/Path/To/Output.gdtf"));

// 或获取为内存数据
TArray64<uint8> OutputData;
if (Zipper->GetData(OutputData))
{
    // OutputData 包含完整的 ZIP 二进制内容
}
```

### 进阶用法 — 使用作用域临时文件解压

```cpp
TSharedRef<FDMXZipper> Zipper = MakeShared<FDMXZipper>();
Zipper->LoadFromFile(TEXT("MyFixture.gdtf"));

{
    // 将 ZIP 内文件解压为临时文件，超出作用域自动删除
    FDMXZipper::FDMXScopedUnzipToTempFile ScopedTemp(Zipper, TEXT("models/fixture.3ds"));

    // 使用临时文件路径（如传给 3D 模型加载器）
    UStaticMesh* Mesh = LoadMeshFromFile(ScopedTemp.TempFilePathAndName);
    
} // 临时文件在此自动删除
```

## Demo 示例

以下示例展示如何使用 `FDMXZipper` 解析一个 `.gdtf` 文件并提取其中的 XML 描述：

### DMXGDTFParser.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "DMXZipper.h"

class FDMXGDTFFileParser
{
public:
    /** 从 .gdtf 文件路径加载并解析 */
    bool LoadFromGDTFFile(const FString& GDTFFilePath);

    /** 从二进制数据加载并解析 */
    bool LoadFromGDTFData(const TArray64<uint8>& RawData);

    /** 获取 XML 描述内容 */
    const FString& GetDescriptionXml() const { return DescriptionXml; }

    /** 获取 ZIP 内所有文件列表 */
    TArray<FString> GetIncludedFiles() const;

private:
    TSharedRef<FDMXZipper> Zipper;
    FString DescriptionXml;
};
```

### DMXGDTFParser.cpp

```cpp
#include "DMXGDTFParser.h"

FDMXGDTFFileParser::FDMXGDTFFileParser()
    : Zipper(MakeShared<FDMXZipper>())
{
}

bool FDMXGDTFFileParser::LoadFromGDTFFile(const FString& GDTFFilePath)
{
    if (!Zipper->LoadFromFile(GDTFFilePath))
    {
        UE_LOG(LogDMXZip, Error, TEXT("Failed to load GDTF file: %s"), *GDTFFilePath);
        return false;
    }

    // GDTF 标准要求 description.xml 位于根目录
    TArray64<uint8> XmlData;
    if (!Zipper->GetFileContent(TEXT("description.xml"), XmlData))
    {
        UE_LOG(LogDMXZip, Error, TEXT("GDTF file missing description.xml: %s"), *GDTFFilePath);
        return false;
    }

    // 转换为 UTF-8 字符串
    FFileHelper::BufferToString(DescriptionXml, XmlData.GetData(), XmlData.Num());
    return true;
}

bool FDMXGDTFFileParser::LoadFromGDTFData(const TArray64<uint8>& RawData)
{
    if (!Zipper->LoadFromData(RawData))
    {
        UE_LOG(LogDMXZip, Error, TEXT("Failed to load GDTF from data"));
        return false;
    }

    TArray64<uint8> XmlData;
    if (!Zipper->GetFileContent(TEXT("description.xml"), XmlData))
    {
        UE_LOG(LogDMXZip, Error, TEXT("GDTF data missing description.xml"));
        return false;
    }

    FFileHelper::BufferToString(DescriptionXml, XmlData.GetData(), XmlData.Num());
    return true;
}

TArray<FString> FDMXGDTFFileParser::GetIncludedFiles() const
{
    return Zipper->GetFiles();
}
```

## 模块依赖

`DMXZip` 模块的依赖非常轻量：

无特殊依赖（仅标准 Core/Engine 等）

`FDMXZipper` 仅使用 `TSharedFromThis`、`FArrayReader`、`FArrayWriter` 等 Core 层类型，无外部模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的打印问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-02-02 | `f5e86e73` | DMXGDTF: Fix potential divide by zero | 修复 GDTF 解析中潜在的除零错误 |
| 2024-09-26 | `62a80188` | DMX: Move the DMXGDTF header from internal to public | 将 DMXGDTF 头文件从内部目录移至公共目录，允许外部模块引用 |

### 维护评价

**维护状态：活跃维护中**

- 插件创建于 2024 年 4 月，属于较新的虚拟制作模块
- 近期持续有编译兼容性改进和 bug 修复（2026 年仍有活跃提交）
- 作为 DMX 插件生态的基础依赖，获得稳定维护
- 标记为 `Hidden: true`，说明它是内部基础设施而非面向最终用户的插件
- **推荐使用**：如果你的项目涉及虚拟制作中的 DMX 灯具控制，此插件是处理 GDTF 文件的标准方式。普通项目无需直接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [GDTF 标准官网](https://gdtf-share.com/)