# Blueprint File Utilities

> A Blueprint library that enables low-level file operations such as Move, Copy, Delete, and Find.

| 属性 | 值 |
|---|---|
| 分类 | Blueprints |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | BlueprintFileUtils (Runtime) |
| 创建时间 | 2017-06-16 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/BlueprintFileUtils) | |

## 用途

BlueprintFileUtils 是一个轻量级的蓝图函数库，把 UE 底层的 `IFileManager` 接口暴露给蓝图使用。它解决的核心问题是：蓝图中无法直接进行文件系统操作（查找、创建、删除、复制、移动文件/目录）。无需编写 C++ 代码，即可在蓝图中完成基础的文件管理任务。

整个 plugin 只有一个类 `UBlueprintFileUtilsBPLibrary`，本质上是对 `IFileManager::Get()` 的薄层封装，每个函数映射一个底层文件操作。

> ⚠️ 需要手动启用：`EnabledByDefault` 为 false，必须在 Edit → Plugins 中手动勾选启用。

## 使用场景

- 你的游戏需要在运行时读取本地文件系统中的配置文件或资源列表 → 用 `FindFiles` / `FindRecursive`
- 你需要在打包后的游戏中让用户选择目录，然后检查目录是否存在 → 用 `DirectoryExists`
- 你做一个关卡编辑器 mod 工具，需要创建/删除用户自定义内容目录 → 用 `MakeDirectory` / `DeleteDirectory`
- 你需要在蓝图中实现文件备份功能 → 用 `CopyFile` / `MoveFile`
- 你需要获取当前操作系统的用户目录路径 → 用 `GetUserDirectory`

## 蓝图用法

所有节点归类在 **FileUtils** 分组下。

### 查找文件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindFiles` | 在指定目录中查找文件，可按扩展名过滤 | `UBlueprintFileUtilsBPLibrary` |
| `FindRecursive` | 递归查找目录及子目录中的文件/目录，支持通配符 | `UBlueprintFileUtilsBPLibrary` |

`FindFiles` 参数：
- `Directory`：绝对路径，如 `C:\Users\Me\Documents`
- `FileExtension`：空字符串表示所有文件，或传 `.txt` / `txt` 过滤扩展名
- 返回 `FoundFiles` 数组 + bool 表示是否找到

`FindRecursive` 参数：
- `StartDirectory`：起始搜索的绝对路径
- `Wildcard`：通配符，如 `*.png`、`*config*`；空则匹配所有
- `bFindFiles`：是否查找文件（默认 true）
- `bFindDirectories`：是否查找目录（默认 false）

### 检查存在

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FileExists` | 检查文件是否存在 | `UBlueprintFileUtilsBPLibrary` |
| `DirectoryExists` | 检查目录是否存在 | `UBlueprintFileUtilsBPLibrary` |

### 目录操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeDirectory` | 创建目录，可选递归创建整棵目录树 | `UBlueprintFileUtilsBPLibrary` |
| `DeleteDirectory` | 删除目录，可选递归删除子目录 | `UBlueprintFileUtilsBPLibrary` |

`MakeDirectory`：`bCreateTree=true` 时会自动创建所有缺失的中间目录。

`DeleteDirectory`：`bDeleteRecursively=false` 且目录非空时，操作会失败。

### 文件操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DeleteFile` | 删除文件 | `UBlueprintFileUtilsBPLibrary` |
| `CopyFile` | 复制文件 | `UBlueprintFileUtilsBPLibrary` |
| `MoveFile` | 移动文件 | `UBlueprintFileUtilsBPLibrary` |

三个函数都有 `bEvenIfReadOnly` 参数，设为 true 可强制操作只读文件。

### 工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUserDirectory` | 获取当前用户的系统目录（Pure 函数，无执行引脚） | `UBlueprintFileUtilsBPLibrary` |

返回平台相关的用户目录，如 Windows 上的 `C:\Users\<用户名>\`。

### 使用示例（蓝图描述）

**示例 1：查找某目录下的所有 PNG 文件**

1. 拖入 `FindFiles` 节点
2. `Directory` 连接到一个 `C:\GameAssets\Screenshots` 字符串变量
3. `FileExtension` 设为 `.png`
4. `FoundFiles` 输出连接到一个 `TArray<FString>` 变量
5. 用 `ForEachLoop` 遍历结果

**示例 2：递归创建目录后复制文件**

1. `MakeDirectory` → `Path` = `C:\Backup\Saves\2024`，`bCreateTree` = true
2. 成功后 → `CopyFile` → `DestFilename` = `C:\Backup\Saves\2024\save.dat`，`SrcFilename` = 原始存档路径

**示例 3：安全删除前检查文件存在**

1. `FileExists` → `Filename` = 目标路径
2. Branch：true → `DeleteFile`；false → 打印警告

## C++ 用法

### 头文件引入

```cpp
#include "BlueprintFileUtilsBPLibrary.h"
```

### 基本用法

所有函数都是 `static`，可直接通过类名调用（来源：`BlueprintFileUtilsBPLibrary.cpp`）：

```cpp
// 查找目录中的文件
TArray<FString> FoundFiles;
bool bFound = UBlueprintFileUtilsBPLibrary::FindFiles(
    TEXT("C:\\Users\\Me\\Pictures"), FoundFiles, TEXT(".png"));

// 递归查找
TArray<FString> AllPaths;
UBlueprintFileUtilsBPLibrary::FindRecursive(
    TEXT("C:\\GameAssets"), AllPaths, TEXT("*.uasset"), true, false);

// 检查文件/目录是否存在
bool bExists = UBlueprintFileUtilsBPLibrary::FileExists(TEXT("C:\\Config\\settings.ini"));
bool bDirExists = UBlueprintFileUtilsBPLibrary::DirectoryExists(TEXT("C:\\Saves"));

// 获取用户目录
FString UserDir = UBlueprintFileUtilsBPLibrary::GetUserDirectory();
// Windows: "C:\Users\<username>\"
```

### 进阶用法

```cpp
// 递归创建目录结构，然后写入文件
FString SavePath = FPaths::Combine(FPlatformProcess::UserDir(), TEXT("MyGame"), TEXT("Saves"));
UBlueprintFileUtilsBPLibrary::MakeDirectory(SavePath, true);

// 文件备份工作流：复制 + 验证
FString BackupPath = SavePath + TEXT(".bak");
bool bCopied = UBlueprintFileUtilsBPLibrary::CopyFile(BackupPath, SavePath);
if (bCopied)
{
    UE_LOG(LogTemp, Log, TEXT("Backup created at: %s"), *BackupPath);
}

// 清理旧备份（强制删除只读文件）
UBlueprintFileUtilsBPLibrary::DeleteFile(BackupPath, true, true);
```

## Demo 示例

### 最小文件管理工具

```cpp
// MyFileHelper.h
#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyFileHelper.generated.h"

UCLASS()
class UMyFileHelper : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 清理目录中所有 .tmp 文件
    UFUNCTION(BlueprintCallable, Category = "FileHelper")
    static int32 CleanupTempFiles(const FString& Directory)
    {
        TArray<FString> TempFiles;
        UBlueprintFileUtilsBPLibrary::FindFiles(Directory, TempFiles, TEXT(".tmp"));

        int32 Deleted = 0;
        for (const FString& File : TempFiles)
        {
            FString FullPath = FPaths::Combine(Directory, File);
            if (UBlueprintFileUtilsBPLibrary::DeleteFile(FullPath))
            {
                Deleted++;
            }
        }
        return Deleted;
    }
};
```

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "BlueprintFileUtils"  // 需要引用此模块
});
```

## 模块依赖

如果你要在自己的模块中调用 `UBlueprintFileUtilsBPLibrary`，需要在 Build.cs 中添加：

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎模块（FString、TArray 等） |
| `BlueprintFileUtils` | 本插件模块，提供文件操作蓝图函数库 |

插件自身的 Private 依赖（无需额外引用）：

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架（本插件实际未使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da7` | [Engine/Plugins] Another batch IWYU updates to reduce number of includes used in files | IWYU（Include What You Use）头文件清理，纯编译优化，无功能变化 |
| 2022-11-07 | `0a10c21f` | Update Release-Engine-Staging from UE5/Main | 分支同步更新，非针对性改动 |
| 2022-09-08 | `5774ff07` | Cleaned up build.cs files by removing include paths already added by UBT | Build.cs 清理，无功能变化 |

### 维护评价

- **创建时间**：2017-06-16，已存在约 9 年
- **最后实质性功能更新**：**从未有过**——自创建以来没有新增任何函数或功能
- **近期改动**：全部是编译/构建层面的维护性更新（IWYU、Build.cs 清理）
- **代码规模**：极小（4 个源文件，1 个类，10 个函数），功能完整且稳定
- **活跃度**：⚠️ **维护不活跃** — 超过 3 年无功能性更新

**综合评价**：这是一个极其简单且功能完整的 wrapper plugin。它把 `IFileManager` 的 10 个常用操作暴露给蓝图，功能自创建以来从未改变。由于底层 `IFileManager` 本身是引擎核心且非常稳定，这个 plugin 缺乏更新并非 bug 信号，而是"功能已经足够"。但需注意：

1. 没有异步版本 — 大文件操作会阻塞游戏线程
2. 没有文件读写功能 — 只有文件管理操作（查找/创建/删除/复制/移动）
3. 没有测试用例
4. `EnabledByDefault=false`，需要手动启用
5. `Slate`/`SlateCore` 依赖看起来是模板残留，实际未使用

**推荐使用**：✅ 如果只需要简单的文件管理操作，推荐使用。如果需要读写文件内容或异步操作，应考虑直接使用 C++ 的 `FFileHelper` 或 `IFileManager`。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/BlueprintFileUtils)
- 官方文档（无）
