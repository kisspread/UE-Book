# Blueprint File Utilities

> A Blueprint library that enables low-level file operations such as Move, Copy, Delete, and Find.

| 属性 | 值 |
|---|---|
| 中文名 | 蓝图文件工具库 |
| 分类 | Blueprints |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlueprintFileUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-01-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/BlueprintFileUtils) | |

## 用途

BlueprintFileUtils 为蓝图提供了直接访问底层文件系统的能力。UE5 蓝图本身不提供跨平台的文件操作节点，而此插件填补了这一空缺——你可以在蓝图中执行文件的查找、复制、移动、删除，以及目录的创建与删除等操作。

它本质上是对 `FPlatformFileManager` 和 `IFileManager` 等引擎文件 API 的蓝图包装（`UBlueprintFunctionLibrary`），让设计师和关卡策划无需编写 C++ 代码即可完成文件 IO 任务。

> ⚠️ 此插件默认未启用（`EnabledByDefault: false`），需在项目设置中手动启用。

## 使用场景

- 你需要在打包后的运行时程序中，通过蓝图读取/管理本地文件系统中的文件
- 你需要在编辑器工具蓝图中批量处理文件（如批量复制资源、清理临时目录）
- 你需要递归搜索某个目录下符合特定扩展名的所有文件
- 你需要检查某个配置文件或资源文件是否存在后再决定后续逻辑

## 蓝图用法

所有函数均位于 `FileUtils` 蓝图分类下，可直接拖入蓝图图表使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindFiles` | 在指定目录中查找文件，可按扩展名过滤 | `UBlueprintFileUtilsBPLibrary` |
| `FindRecursive` | 递归搜索目录及子目录，支持通配符，可选择查找文件和/或目录 | `UBlueprintFileUtilsBPLibrary` |
| `FileExists` | 检查文件是否存在 | `UBlueprintFileUtilsBPLibrary` |
| `DirectoryExists` | 检查目录是否存在 | `UBlueprintFileUtilsBPLibrary` |
| `MakeDirectory` | 创建目录，可选是否递归创建整棵目录树 | `UBlueprintFileUtilsBPLibrary` |
| `DeleteDirectory` | 删除目录，可选是否递归删除子目录和文件 | `UBlueprintFileUtilsBPLibrary` |
| `DeleteFile` | 删除文件，可选跳过只读检查 | `UBlueprintFileUtilsBPLibrary` |
| `CopyFile` | 复制文件，可选覆盖已有文件和跳过只读 | `UBlueprintFileUtilsBPLibrary` |
| `MoveFile` | 移动文件，可选覆盖已有文件和跳过只读 | `UBlueprintFileUtilsBPLibrary` |
| `GetUserDirectory` | 获取用户目录（如"我的文档"或用户主目录） | `UBlueprintFileUtilsBPLibrary` |

### 使用示例

**示例 1：查找目录下所有 PNG 文件**

1. 拖入 `FindFiles` 节点
2. `Directory` 连接一个字符串变量，如 `"C:\MyProject\Textures"`
3. `FileExtension` 设为 `".png"` 或 `"png"`
4. `FoundFiles` 输出的数组即为匹配的所有文件完整路径
5. 返回值为 `true` 表示找到了至少一个文件

**示例 2：递归搜索并清理临时目录**

1. 拖入 `FindRecursive` 节点，`StartDirectory` 设为项目临时目录
2. `Wildcard` 设为 `"*.tmp"`，`bFindFiles` 勾选，`bFindDirectories` 取消勾选
3. 将 `FoundPaths` 数组接入 `ForEachLoop`
4. 循环体内对每个路径调用 `DeleteFile`，`bEvenIfReadOnly` 勾选以确保清理只读文件
5. 最后调用 `DeleteDirectory`，`bDeleteRecursively` 勾选以删除空的临时目录

**示例 3：安全地准备输出目录**

1. 调用 `DirectoryExists` 检查目标目录是否存在
2. 如果不存在，调用 `MakeDirectory`，`bCreateTree` 勾选以递归创建完整路径
3. 后续即可安全地写入文件

## C++ 用法

### 头文件引入

```cpp
#include "BlueprintFileUtilsBPLibrary.h"
```

### 基本用法

由于所有函数均为 `static`，无需实例化即可调用：

```cpp
// 检查文件是否存在
FString FilePath = TEXT("C:/MyProject/Config/GameSettings.ini");
bool bExists = UBlueprintFileUtilsBPLibrary::FileExists(FilePath);

// 创建目录（递归创建整棵目录树）
FString NewDir = TEXT("C:/MyProject/Output/2024/January");
bool bCreated = UBlueprintFileUtilsBPLibrary::MakeDirectory(NewDir, /*bCreateTree=*/ true);

// 复制文件（覆盖已有文件）
FString SrcFile = TEXT("C:/MyProject/Assets/Template.uasset");
FString DestFile = TEXT("C:/MyProject/Output/NewAsset.uasset");
bool bCopied = UBlueprintFileUtilsBPLibrary::CopyFile(DestFile, SrcFile, /*bReplace=*/ true);
```

### 进阶用法

```cpp
// 递归查找所有 .json 文件
FString SearchDir = TEXT("C:/MyProject/Data");
TArray<FString> JsonFiles;
bool bFound = UBlueprintFileUtilsBPLibrary::FindRecursive(
    SearchDir,
    JsonFiles,
    TEXT("*.json"),
    /*bFindFiles=*/ true,
    /*bFindDirectories=*/ false
);

if (bFound)
{
    for (const FString& JsonFile : JsonFiles)
    {
        UE_LOG(LogTemp, Log, TEXT("Found JSON: %s"), *JsonFile);
    }
}

// 获取用户目录并在其下创建应用数据目录
FString UserDir = UBlueprintFileUtilsBPLibrary::GetUserDirectory();
FString AppDataDir = FPaths::Combine(UserDir, TEXT("MyGame"), TEXT("Saves"));
UBlueprintFileUtilsBPLibrary::MakeDirectory(AppDataDir, true);
```

## Demo 示例

**MyFileTool.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "BlueprintFileUtilsBPLibrary.h"
#include "MyFileTool.generated.h"

UCLASS()
class UMyFileTool : public UObject
{
    GENERATED_BODY()

public:
    /** 备份指定目录下所有 .ini 文件到备份目录 */
    UFUNCTION(BlueprintCallable, Category = "FileTool")
    static bool BackupIniFiles(const FString& SourceDir, const FString& BackupDir);
};
```

**MyFileTool.cpp**

```cpp
#include "MyFileTool.h"

bool UMyFileTool::BackupIniFiles(const FString& SourceDir, const FString& BackupDir)
{
    // 确保备份目录存在
    if (!UBlueprintFileUtilsBPLibrary::DirectoryExists(BackupDir))
    {
        UBlueprintFileUtilsBPLibrary::MakeDirectory(BackupDir, true);
    }

    // 查找所有 .ini 文件
    TArray<FString> IniFiles;
    if (!UBlueprintFileUtilsBPLibrary::FindFiles(SourceDir, IniFiles, TEXT(".ini")))
    {
        return false;
    }

    // 逐个复制到备份目录
    int32 SuccessCount = 0;
    for (const FString& IniFile : IniFiles)
    {
        FString Filename = FPaths::GetCleanFilename(IniFile);
        FString DestPath = FPaths::Combine(BackupDir, Filename);

        if (UBlueprintFileUtilsBPLibrary::CopyFile(DestPath, IniFile))
        {
            SuccessCount++;
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Backed up %d of %d .ini files"), SuccessCount, IniFiles.Num());
    return SuccessCount == IniFiles.Num();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。

插件自身的 `Build.cs` 仅依赖引擎核心模块，无额外第三方或引擎子模块依赖。你的项目模块如果需要在 C++ 中使用此库，只需在 `Build.cs` 中添加 `"BlueprintFileUtils"` 到 `PublicDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件批量变更，无实际功能改动 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件元数据中的链接更新为 HTTPS 协议 |
| 2022-09-09 | `cb0456c6` | Cleaned up build.cs files by removing any include paths that were already being added by UBT. | 清理 Build.cs 中冗余的 include 路径 |
| 2021-03-18 | `83ac43b8` | Remove UE4 references in BlueprintFileUtilsBPLibrary.h | 移除头文件中的 UE4 旧命名引用，适配 UE5 |

### 维护评价

⚠️ **维护不活跃，可能废弃。**

该插件自 2020 年创建以来，从未有过功能性更新。所有后续提交均为引擎范围的批量维护（链接协议更新、Build.cs 清理、UE4→UE5 重命名）。最近一次提交距今已超过 **2 年**。

- **默认未启用**（`EnabledByDefault: false`），表明 Epic 不认为这是常规项目需要的功能
- 功能非常基础，没有批量操作优化、异步文件操作、路径安全校验等现代特性
- 不过由于功能简单且稳定，当前代码仍可正常工作

**建议**：如果你只需要简单的文件操作且不想引入额外依赖，此插件仍然可用。但如果需要更完善的文件操作能力，建议考虑直接在 C++ 中使用 `FPlatformFileManager` / `IFileManager`，或寻找社区维护的替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/BlueprintFileUtils)
- 官方文档：无