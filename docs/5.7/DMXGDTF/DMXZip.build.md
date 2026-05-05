# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

DMXGDTF 插件实现了 **GDTF（General Device Type Format）标准**，这是灯光行业用于描述 DMX 灯具设备的通用文件格式。GDTF 文件本质上是包含 XML 描述和 3D 模型资源的 ZIP 压缩包。

该插件解决的核心问题：
- **解析 GDTF 文件**：将 `.gdtf` 文件（ZIP 格式）解压并解析为 UE 内部数据结构
- **ZIP 文件操作**：提供专门的 ZIP 读写工具，用于处理 GDTF 和 MVR 等 DMX 相关的压缩文件格式
- **数据结构映射**：将 GDTF 标准中的设备类型、DMX 模式、通道定义等映射为 Unreal Engine 类型

插件被标记为 `Hidden: true`，说明它是 DMX 插件生态的内部依赖，不直接暴露给最终用户。

## 使用场景

- 你在做虚拟制片项目，需要导入 GDTF 格式的灯具定义 → 用 DMXGDTF 解析
- 你需要读取或创建 GDTF/MVR 格式的 ZIP 压缩包 → 用 DMXZip 模块
- 你在开发自定义 DMX 灯具管理工具，需要程序化操作 GDTF 文件 → 用此插件的 API

## 蓝图用法

DMXZip 模块是纯 C++ 运行时模块，不暴露蓝图节点。DMXGDTF 主模块可能包含蓝图接口，但当前未提供其源码。

## C++ 用法

### 头文件引入

```cpp
#include "DMXZipper.h"
```

### 基本用法

从头文件注释中提取的标准用法：

```cpp
// 加载并操作 GDTF/MVR ZIP 文件
bool DoStuffWithZip(const FString& ZipFileName)
{
    FDMXZipper Zipper;
    
    // 从文件加载 ZIP
    Zipper.LoadFromFile(ZipFileName);

    // 添加文件到 ZIP（支持相对路径）
    Zipper.AddFile("hello/world", { 'A', 'B', 'C' });
    Zipper.AddFile("test001", { '0', '1', '2', '3', 'X' }, false); // 不压缩
    Zipper.AddFile("a/b/c/d/e/test002", { 80, 90, 100, 110, 111, 112, 113 });

    // 添加大文件（如 3D 模型）
    TArray64<uint8> BigFile;
    if (FFileHelper::LoadFileToArray(BigFile, TEXT("D:/SM_MatPreviewMesh_01.stl")))
    {
        Zipper.AddFile("Meshes/Mesh.stl", BigFile);
    }

    // 保存 ZIP 文件
    if (!Zipper.SaveToFile(ZipFileName))
    {
        return false;
    }

    return true;
}
```

### 进阶用法

```cpp
// 从内存数据加载 ZIP（适用于网络下载或嵌入式数据）
TArray64<uint8> RawZipData = /* ... */;
FDMXZipper Zipper;
if (Zipper.LoadFromData(RawZipData))
{
    // 获取 ZIP 内所有文件列表
    TArray<FString> FileNames = Zipper.GetFiles();
    
    // 读取特定文件内容
    TArray64<uint8> FileData;
    if (Zipper.GetFileContent("description.xml", FileData))
    {
        // 处理 GDTF XML 描述文件
    }
}

// 使用作用域守卫将 ZIP 内文件解压为临时文件
{
    FDMXZipper::FDMXScopedUnzipToTempFile ScopedTemp(Zipper.ToSharedRef(), "models/mesh.3ds");
    // 临时文件路径
    FString TempPath = ScopedTemp.TempFilePathAndName;
    // 使用临时文件...
} // 离开作用域时自动删除临时文件
```

## Demo 示例

```cpp
// GDTFFileHelper.h
#pragma once

#include "CoreMinimal.h"

class FDMXZipper;

class FGDTFFileHelper
{
public:
    /** 列出 GDTF 文件中的所有资源 */
    static TArray<FString> ListGDTFContents(const FString& GDTFFilePath);
    
    /** 从 GDTF 文件提取 XML 描述 */
    static bool ExtractDescription(const FString& GDTFFilePath, FString& OutXML);
};
```

```cpp
// GDTFFileHelper.cpp
#include "GDTFFileHelper.h"
#include "DMXZipper.h"

TArray<FString> FGDTFFileHelper::ListGDTFContents(const FString& GDTFFilePath)
{
    FDMXZipper Zipper;
    if (!Zipper.LoadFromFile(GDTFFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load GDTF file: %s"), *GDTFFilePath);
        return {};
    }
    
    return Zipper.GetFiles();
}

bool FGDTFFileHelper::ExtractDescription(const FString& GDTFFilePath, FString& OutXML)
{
    FDMXZipper Zipper;
    if (!Zipper.LoadFromFile(GDTFFilePath))
    {
        return false;
    }
    
    TArray64<uint8> XMLData;
    if (!Zipper.GetFileContent("description.xml", XMLData))
    {
        UE_LOG(LogTemp, Warning, TEXT("GDTF file does not contain description.xml"));
        return false;
    }
    
    // 转换为字符串
    FUTF8ToTCHAR Converter(reinterpret_cast<const ANSICHAR*>(XMLData.GetData()), XMLData.Num());
    OutXML = FString(Converter.Length(), Converter.Get());
    
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

```
- 8e75e2dae524 DMX - Add GDTF export functinality, unit testing, improve GDTF data structure
  → 新增 GDTF 导出功能，添加单元测试，改进 GDTF 数据结构
- 390e9e3124a7 DMX - Upgrade to a new GDTF implementation, initial dev version. UDMXImportGDTF now only holds the raw GDTF data, its GDTF description is deprecated. DMXGDTF now holds the GDTF standard in its own resuable plugin, and can be initialized from raw data.
  → 重大重构：升级到新的 GDTF 实现，将 GDTF 标准独立为可复用插件
```

### 维护评价

- **活跃维护**：插件创建于 2024 年 4 月，至今约 1 年，属于较新的插件
- **开发阶段**：从 commit 信息看，插件仍在积极开发中（"initial dev version"）
- **架构演进**：经历了重大重构，从旧的 `UDMXImportGDTF` 迁移到独立的 DMXGDTF 插件
- **推荐使用**：作为 Epic 官方维护的 Virtual Production 工具链一部分，适合在 DMX/灯光项目中使用，但需注意 API 可能随版本变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [官方文档]()（暂无）

---

# DMX Zip 模块

> Zip reader/writer for DMX specific Zip Files such as MVR and GDTF

## 模块概述

DMXZip 是一个轻量级的 ZIP 文件读写模块，专门为 DMX 领域的文件格式设计。它支持：
- **GDTF 文件**：灯具设备描述格式（.gdtf）
- **MVR 文件**：My Virtual Rig 格式（.mvr）

该模块不依赖第三方 ZIP 库，使用 UE 内置的序列化功能实现。

## 核心类

### FDMXZipper

ZIP 文件操作的核心类，继承自 `TSharedFromThis` 以支持智能指针共享。

#### 公共接口

| 方法 | 说明 |
|---|---|
| `LoadFromFile(Filename)` | 从磁盘文件加载 ZIP |
| `LoadFromData(Data)` | 从内存数据加载 ZIP |
| `SaveToFile(Filename)` | 保存 ZIP 到磁盘文件 |
| `GetData(OutData)` | 获取 ZIP 的内存数据 |
| `GetFiles()` | 获取 ZIP 内所有文件名列表 |
| `AddFile(Path, Data, bCompress)` | 添加文件到 ZIP |
| `GetFileContent(Filename, OutData)` | 读取 ZIP 内指定文件的内容 |

#### FDMXScopedUnzipToTempFile

作用域守卫结构体，用于将 ZIP 内文件临时解压到磁盘，离开作用域时自动清理。

```cpp
struct FDMXScopedUnzipToTempFile
{
    FDMXScopedUnzipToTempFile(const TSharedRef<FDMXZipper>& DMXZipper, const FString& FilenameInZip);
    ~FDMXScopedUnzipToTempFile();
    
    FString TempFilePathAndName; // 临时文件的绝对路径
};
```

## 内部实现细节

- **Central Directory 解析**：标准 ZIP 文件结构解析
- **压缩支持**：可选择是否压缩添加的文件（`bCompress` 参数）
- **路径处理**：支持相对路径和嵌套目录结构
- **大文件支持**：使用 `TArray64<uint8>` 支持超过 4GB 的文件

## 典型使用流程

```
1. LoadFromFile() 或 LoadFromData() 加载 ZIP
2. GetFiles() 列出内容
3. GetFileContent() 读取需要的文件
4. AddFile() 添加新文件（如需修改）
5. SaveToFile() 或 GetData() 保存结果
```