# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types

| 属性 | 值 |
|---|---|
| 中文名 | GDTF标准实现 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

本插件为虚幻引擎提供了 GDTF (General Device Type Format) 标准的完整实现。GDTF 是用于描述舞台和娱乐照明设备（如灯具、LED 面板）的标准化 XML 格式。本插件将 GDTF 文件中的设备定义（包括 3D 模型、DMX 通道映射、控制模式等）解析并转化为引擎内可用的 C++ 对象和资产，解决了在虚拟制作流程中导入和使用行业标准灯具数据格式的问题。

## 使用场景

- **虚拟舞台/演唱会制作**：在 Unreal Engine 的虚拟制片环境中，导入灯具厂商提供的 GDTF 文件，精确控制虚拟场景中的 DMX 灯具，使其行为与真实设备一致。
- **预可视化 (Previz)**：在项目前期，使用标准 GDTF 文件快速搭建灯光设备库，进行灯光布局和效果预览。
- **数据驱动照明系统**：基于 GDTF 标准构建自定义的照明控制系统，利用插件解析的数据来驱动灯具行为。

## 模块列表

| 模块 | 用途 |
|---|---|
| `DMXGDTF` | **核心模块**。提供 GDTF 数据结构、XML 解析器和内存中的对象模型（如 `UDMXGDTFRoot`, `UDMXGDTFFixtureType`）。 |
| `DMXGDTFTests` | **测试模块**。包含 GDTF 解析器和数据正确性的自动化测试用例。 |
| `DMXZip` | **辅助模块**。处理包含 GDTF 文件和相关资源的 `.gdtf` ZIP 压缩包。 |

## 蓝图用法

本插件的蓝图接口主要用于查询和操作解析后的 GDTF 数据，而非文件解析本身。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create GDTF Root` | 静态函数，创建一个新的 `UDMXGDTFRoot` 对象实例。 | `UDMXGDTFRoot` |
| `Write GDTF to File` | 静态函数，将 `UDMXGDTFRoot` 对象序列化并写入 GDTF 文件。 | `UDMXGDTFRoot` |
| `Get Fixture Types` | 获取 GDTF 设备类型列表。 | `UDMXGDTFRoot` |
| `Get Name` | 获取设备的名称。 | `UDMXGDTFFixtureType` |
| `Get Geometry` | 获取设备的几何形状信息。 | `UDMXGDTFFixtureType` |

### 使用示例（蓝图描述）
1.  **加载并查询 GDTF 数据**：通过 C++ 获得解析后的 `UDMXGDTFRoot` 对象后，在蓝图中调用其 `Get Fixture Types` 节点获取所有设备类型，然后遍历列表并调用 `Get Name` 等节点获取具体信息。
2.  **程序化生成 GDTF**：在蓝图中创建 `UDMXGDTFRoot` 对象，向其中添加 `UDMXGDTFFixtureType`，设置其属性，最后调用 `Write GDTF to File` 导出。

## C++ 用法

核心用法是通过 `FDMXGDTFParser` 解析 GDTF 数据，并操作解析后生成的 `UDMXGDTFRoot` 对象。

### 头文件引入

```cpp
#include "DMXGDTF.h"
#include "DMXGDTFRoot.h"
#include "DMXGDTFFixtureType.h"
#include "Serialization/DMXGDTFParser.h"
```

### 基本用法

从文件解析 GDTF 数据。
（来源：`DMXGDTFTests/DMXGDTFParserTest.cpp`）

```cpp
// 1. 读取 GDTF 文件内容
FString GDTFContent;
FFileHelper::LoadFileToString(GDTFContent, TEXT("path/to/your/file.gdtf"));

// 2. 创建解析器并执行解析
FDMXGDTFParser Parser;
UDMXGDTFRoot* Root = Parser.Parse(*GDTFContent);

// 3. 检查解析结果并访问数据
if (Root)
{
    // 获取并遍历所有设备类型
    for (UDMXGDTFFixtureType* FixtureType : Root->GetFixtureTypes())
    {
        FString Name = FixtureType->GetName();
        // ... 对设备类型进行其他操作
    }
}
```

### 进阶用法

遍历 GDTF 树状结构。
（来源：`DMXGDTFTests/DMXGDTFNodesTest.cpp`）

```cpp
void TraverseGDTFTree(UDMXGDTFBaseNode* Node, int32 Depth)
{
    if (!Node) return;
    
    // 打印当前节点名称和深度
    UE_LOG(LogTemp, Log, TEXT("%*s Node: %s"), Depth * 2, TEXT(""), *Node->GetName());
    
    // 递归遍历子节点
    for (UDMXGDTFBaseNode* Child : Node->GetChildren())
    {
        TraverseGDTFTree(Child, Depth + 1);
    }
}

// 使用示例
TraverseGDTFTree(Root, 0);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何加载并遍历 GDTF 文件。

**头文件 (`GDTFDemo.h`):**
```cpp
#pragma once
#include "CoreMinimal.h"

class UDMXGDTFRoot;
class UDMXGDTFFixtureType;

class FGDTFDemo
{
public:
    void LoadAndAnalyzeGDTF(const FString& FilePath);
};
```

**源文件 (`GDTFDemo.cpp`):**
```cpp
#include "GDTFDemo.h"
#include "DMXGDTF.h"
#include "DMXGDTFRoot.h"
#include "DMXGDTFFixtureType.h"
#include "Serialization/DMXGDTFParser.h"
#include "Misc/FileHelper.h"

void FGDTFDemo::LoadAndAnalyzeGDTF(const FString& FilePath)
{
    FString FileContent;
    if (!FFileHelper::LoadFileToString(FileContent, *FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load GDTF file: %s"), *FilePath);
        return;
    }

    FDMXGDTFParser Parser;
    UDMXGDTFRoot* GDTFRoot = Parser.Parse(*FileContent);

    if (GDTFRoot)
    {
        UE_LOG(LogTemp, Log, TEXT("GDTF File Parsed Successfully."));
        const TArray<UDMXGDTFFixtureType*>& FixtureTypes = GDTFRoot->GetFixtureTypes();
        UE_LOG(LogTemp, Log, TEXT("Found %d fixture types."), FixtureTypes.Num());

        for (const UDMXGDTFFixtureType* Fixture : FixtureTypes)
        {
            if (Fixture)
            {
                UE_LOG(LogTemp, Log, TEXT("  - Fixture Type: %s"), *Fixture->GetName());
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse GDTF content."));
    }
}
```

## 模块依赖

使用 `DMXGDTF` 模块时，你的 `Build.cs` 文件需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `CommonUI` | GDTF 节点可能依赖的公共 UI 框架类型 |
| `Json` | 用于处理 GDTF 解析过程中的中间数据（如元数据） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式化字符串中32位与64位说明符的匹配问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移至新的UE_LOGF宏。 |
| 2026-02-02 | `f5e86e73` | DMXGDTF: Fix potential divide by zero | 修复GDTF模块中潜在的除零错误。 |
| 2024-09-26 | `62a80188` | DMX: Move the DMXGDTF header from internal to public | 将DMXGDTF头文件从内部目录移动至公共目录。 |

### 维护评价

**维护中**。插件创建于2024年4月，近期（2026年）仍有针对代码质量、健壮性和引擎版本兼容性的修复提交。虽然最近的更新主要是维护性修复而非新功能，但考虑到 GDTF 是一个成熟的标准，且插件作为基础设施层，稳定性和正确性比频繁的功能迭代更重要。插件当前状态稳定，推荐用于依赖 GDTF 标准的虚拟制作项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [GDTF 官方规范](https://gdtf-share.com/)（外部链接，非官方文档）
- **模块子文档**:
    - [DMXGDTF 模块](./DMXGDTF.md)
    - [DMXGDTFTests 模块](./DMXGDTFTests.md)
    - [DMXZip 模块](./DMXZip.md)