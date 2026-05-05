# SQLite

> Provides a lightweight C++ wrapper for creating and manipulating SQLite databases. It uses the sqlite C library please refer to Engine/Source/ThirdParty/Licenses/SQLite_v3.47.1.license for license details.

| 属性 | 值 |
|---|---|
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | 否 |
| 模块 | SQLiteCore (Runtime) |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（~7年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteCore) | |

## 用途

SQLiteCore 将 SQLite3 数据库引擎嵌入到 Unreal Engine 中，提供面向 UE 的 C++ 封装层。它解决了在引擎运行时进行**轻量级本地数据持久化**的需求——无需部署独立数据库服务器，即可在本地文件中存储结构化数据。

Plugin 内嵌了完整的 SQLite3 源码（v3.47.1），并通过自定义 VFS（Virtual File System）层对接 UE 的文件 I/O，使 SQLite 在 UE 支持的所有平台上都能工作。

**注意**：默认情况下启用的编译选项包括 FTS4/FTS5（全文搜索）、RTree（空间索引）、JSON1 扩展、ICU（Unicode 排序，如可用）。

## 使用场景

- 你需要在游戏运行时存储和查询本地配置、存档元数据、成就记录等结构化数据 → 用 SQLiteCore
- 你的编辑器工具需要一个轻量级嵌入式数据库来存储索引、缓存或元信息 → 用 SQLiteCore
- 你需要全文搜索功能来实现游戏内物品/日志检索 → SQLiteCore 内置 FTS5

**限制**：`.uplugin` 中 `EnabledByDefault: false`，需要手动启用。且 `SupportedPrograms` 仅限 `UnrealMultiUserServer`、`CoopMultiUserServer`、`UnrealMultiUserSlateServer`、`UnrealRecoverySvc`、`LiveLinkHub`，**不包含通用游戏目标**。要在普通游戏项目中使用，需要修改 `.uplugin` 或自行构建模块。

## 蓝图用法

SQLiteCore 是纯 C++ API，**没有暴露任何蓝图节点**。所有操作都需要在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteDatabase.h"
// SQLitePreparedStatement.h 已被 SQLiteDatabase.h 包含
```

### 基本用法

以下示例来自官方测试用例 `Source/SQLiteCore/Private/Tests/SQLiteTest.cpp`：

**打开数据库、建表、插入数据、查询**

```cpp
#include "SQLiteDatabase.h"

// 打开（或创建）数据库文件
FString Path = FPaths::ConvertRelativePathToFull(
    FPaths::ProjectSavedDir() / TEXT("MyData.db"));

FSQLiteDatabase Db;
bool bOk = Db.Open(*Path, ESQLiteDatabaseOpenMode::ReadWriteCreate);
// bOk == true 表示成功

// 创建表
Db.Execute(TEXT("CREATE TABLE users (id INTEGER NOT NULL, name TEXT, title TEXT)"));

// 插入记录
Db.Execute(TEXT("INSERT INTO users (id, name, title) VALUES (1, 'John', 'Manager')"));
Db.Execute(TEXT("INSERT INTO users (id, name, title) VALUES (2, 'Mark', 'Engineer')"));

// 查询并遍历结果
Db.Execute(TEXT("SELECT * FROM users ORDER BY id"),
    [](const FSQLitePreparedStatement& Row) -> ESQLitePreparedStatementExecuteRowResult
{
    int64 Id;
    FString Name, Title;
    Row.GetColumnValueByName(TEXT("id"), Id);
    Row.GetColumnValueByName(TEXT("name"), Name);
    Row.GetColumnValueByName(TEXT("title"), Title);

    UE_LOG(LogTemp, Log, TEXT("User: %lld - %s (%s)"), Id, *Name, *Title);
    return ESQLitePreparedStatementExecuteRowResult::Continue;  // 继续下一行
});

// 关闭数据库
Db.Close();
```

**注意**：`ReadWrite` 模式在文件不存在时会失败；`ReadWriteCreate` 会自动创建文件。

### 进阶用法

#### 使用 Prepared Statement 进行参数化查询

```cpp
// 使用绑定参数的预编译语句
FSQLitePreparedStatement Stmt(Db,
    TEXT("INSERT INTO users (id, name, title) VALUES (?1, ?2, ?3)"));

Stmt.SetBindingValueByIndex(1, (int64)3);
Stmt.SetBindingValueByIndex(2, TEXT("Alice"));
Stmt.SetBindingValueByIndex(3, TEXT("Designer"));
Stmt.Execute();
Stmt.Destroy();
```

#### 类型安全的 Prepared Statement（使用宏）

SQLiteCore 提供了类型安全的 Prepared Statement 宏系统，可以在编译期检查绑定参数和列类型：

```cpp
// 定义类型安全的语句类型
SQLITE_PREPARED_STATEMENT(
    FInsertUserStatement,
    "INSERT INTO users (id, name, title) VALUES (?1, ?2, ?3)",
    SQLITE_PREPARED_STATEMENT_COLUMNS(),                           // 无返回列
    SQLITE_PREPARED_STATEMENT_BINDINGS(int64, FString, FString)    // 三个绑定参数
);

// 使用
FInsertUserStatement InsertStmt(Db);
InsertStmt.BindAndExecute(42, TEXT("Bob"), TEXT("Lead"));

// 定义带返回列的查询语句
SQLITE_PREPARED_STATEMENT(
    FSelectUserById,
    "SELECT id, name, title FROM users WHERE id = ?1",
    SQLITE_PREPARED_STATEMENT_COLUMNS(int64, FString, FString),
    SQLITE_PREPARED_STATEMENT_BINDINGS(int64)
);

FSelectUserById SelectStmt(Db);
int64 Id; FString Name, Title;
SelectStmt.BindAndExecuteSingle(42, Id, Name, Title);
```

#### 数据库版本管理

```cpp
// 设置/获取 user version（常用于数据库 schema 迁移）
int32 Version = 0;
Db.GetUserVersion(Version);
if (Version == 0)
{
    Db.Execute(TEXT("CREATE TABLE ..."));
    Db.SetUserVersion(1);
}

// 完整性检查
bool bHealthy = Db.PerformQuickIntegrityCheck();
```

#### 支持的绑定/列值类型

| 类型 | 绑定（SetBindingValue） | 读取（GetColumnValue） |
|---|---|---|
| 整数 | `int8`, `uint8`, `int16`, `uint16`, `int32`, `uint32`, `int64`, `uint64` | 同左 |
| 浮点 | `float`, `double` | 同左 |
| 字符串 | `TCHAR*`, `FString`, `FName`, `FText` | 同左 |
| 二进制 | `TArrayView<const uint8>`, `void*`, `FGuid` | `TArray<uint8>`, `FGuid` |
| 时间 | `FDateTime` | 同左 |
| 枚举 | 任意 `enum class`（自动转为底层整数类型） | 同左 |
| NULL | 无参调用 `SetBindingValueByName/ByIndex` | - |

### 打开模式

| 模式 | 说明 |
|---|---|
| `ESQLiteDatabaseOpenMode::ReadOnly` | 只读打开，文件不存在则失败 |
| `ESQLiteDatabaseOpenMode::ReadWrite` | 读写打开，文件不存在则失败 |
| `ESQLiteDatabaseOpenMode::ReadWriteCreate` | 读写打开，文件不存在则创建 |

## Demo 示例

### 完整的最小示例

**MyModule.Build.cs** 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "SQLiteCore"
});
```

**MyClass.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "SQLiteDatabase.h"

class FMyDatabase
{
public:
    bool Open(const FString& Path);
    void Close();
    bool InsertUser(int64 Id, const FString& Name);
    bool GetUser(int64 Id, FString& OutName);

private:
    FSQLiteDatabase Database;
};
```

**MyClass.cpp**：

```cpp
#include "MyClass.h"

bool FMyDatabase::Open(const FString& Path)
{
    if (!Database.Open(*Path, ESQLiteDatabaseOpenMode::ReadWriteCreate))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open database: %s"), *Database.GetLastError());
        return false;
    }
    Database.Execute(TEXT("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"));
    return true;
}

void FMyDatabase::Close()
{
    Database.Close();
}

bool FMyDatabase::InsertUser(int64 Id, const FString& Name)
{
    FSQLitePreparedStatement Stmt(Database,
        TEXT("INSERT OR REPLACE INTO users (id, name) VALUES (?1, ?2)"));
    return Stmt.SetBindingValueByIndex(1, Id)
        && Stmt.SetBindingValueByIndex(2, Name)
        && Stmt.Execute();
}

bool FMyDatabase::GetUser(int64 Id, FString& OutName)
{
    FSQLitePreparedStatement Stmt(Database,
        TEXT("SELECT name FROM users WHERE id = ?1"));
    Stmt.SetBindingValueByIndex(1, Id);
    if (Stmt.Step() == ESQLitePreparedStatementStepResult::Row)
    {
        return Stmt.GetColumnValueByName(TEXT("name"), OutName);
    }
    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心模块（FString, TArray 等） |
| `TraceLog` | 追踪日志 |

使用方只需在 Build.cs 中添加 `SQLiteCore` 依赖即可，`Core` 和 `TraceLog` 会自动传递。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-04-23 | `736bd5e` | Used LyraGame build target to find and convert all files to have dllstorage | 将导出符号标记改为 `dllstorage`，适配 DLL 构建目标 |
| 2025-01-10 | `48a0ff8` | Move sqlite3.h into ThirdParty folder | 重组目录结构，将 SQLite 头文件移入 ThirdParty |
| 2025-01-10 | `3863862` | Backout the backout so that we can keep CIS happy | 修复 CI 链接器问题的回退操作 |

### 维护评价

- **创建时间**：2019 年 1 月（~7 年历史）
- **近期活跃度**：2025 年 1 月和 4 月有更新，属于**活跃维护**
- **更新性质**：主要是构建系统/符号导出修复，非功能新增
- **特殊限制**：`SupportedPrograms` 仅限特定服务器/工具程序，不包含通用游戏
- **推荐度**：如果你的项目属于 `SupportedPrograms` 范围，或愿意自行调整 `.uplugin`，这是一个成熟可靠的嵌入式数据库方案。对于普通游戏项目，可能需要评估是否修改 plugin 配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Database/SQLiteCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/Database/SQLiteCore/Source/SQLiteCore/Private/Tests/SQLiteTest.cpp)
- [SQLite 官方文档](https://www.sqlite.org/docs.html)
