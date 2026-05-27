# SQLiteCore

> Provides a lightweight C++ wrapper for creating and manipulating SQLite databases. It uses the sqlite C library please refer to Engine/Source/ThirdParty/Licenses/SQLite_v3.47.1.license for license details.

| 属性 | 值 |
|---|---|
| 中文名 | SQLite 数据库 |
| 分类 | Database |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SQLiteCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteCore) | |

## 用途

SQLiteCore 是 Epic 为 Unreal Engine 内部工具链提供的 SQLite 数据库 C++ 封装层。它将 SQLite 原始的 C API（`sqlite3.h`）包装为符合 UE 代码风格的 C++ 类，提供类型安全的数据库操作、预编译语句（Prepared Statement）绑定与查询等能力。

**核心价值**：为 UE 内部服务程序（如 Multi-User Server、LiveLink Hub、Recovery Service 等）提供轻量级本地持久化存储，不需要依赖外部数据库服务器。`EnabledByDefault=false` 且 `SupportedPrograms` 限定为特定服务程序，说明这是一个面向内部基础设施的插件，不面向普通游戏项目。

## 使用场景

- 你在开发 Multi-User Server 或 LiveLink Hub 等 UE 内部服务程序，需要一个轻量级嵌入式数据库存储配置或状态 → 使用 SQLiteCore
- 你需要在 C++ 中操作 `.db` 文件（创建表、插入/查询数据、使用预编译语句提升性能） → 使用 SQLiteCore
- 你不需要网络数据库，只需要单进程内嵌的键值/表格式存储 → 使用 SQLiteCore

> **注意**：此插件默认未启用（`EnabledByDefault: false`），且仅支持特定程序（`SupportedPrograms`）。若要在自定义项目中使用，需手动在 `.uproject` 中启用，并确保目标程序类型匹配。

## 蓝图用法

此插件**不包含任何 Blueprint 暴露的 API**（无 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`），是纯 C++ API。

## C++ 用法

### 头文件引入

```cpp
#include "SQLiteDatabase.h"
#include "SQLitePreparedStatement.h"
#include "SQLiteTypes.h"
```

### 基本用法 — 打开数据库与执行简单语句

```cpp
// 创建并打开数据库
FSQLiteDatabase Database;
if (Database.Open(TEXT("/path/to/my.db"), ESQLiteDatabaseOpenMode::ReadWriteCreate))
{
    // 创建表
    Database.Execute(TEXT("CREATE TABLE IF NOT EXISTS Players (Id INTEGER PRIMARY KEY, Name TEXT, Score REAL)"));
    
    // 插入数据
    Database.Execute(TEXT("INSERT INTO Players (Name, Score) VALUES ('Alice', 95.5)"));
    
    // 获取最后插入的行 ID
    int64 LastRowId = Database.GetLastInsertRowId();
    
    // 查询并枚举结果
    int64 RowCount = Database.Execute(TEXT("SELECT Id, Name, Score FROM Players"), 
        [](const FSQLitePreparedStatement& Statement) -> ESQLitePreparedStatementExecuteRowResult
        {
            int32 Id = 0;
            FString Name;
            float Score = 0.0f;
            
            Statement.GetColumnValueByIndex(0, Id);
            Statement.GetColumnValueByIndex(1, Name);
            Statement.GetColumnValueByIndex(2, Score);
            
            UE_LOG(LogTemp, Log, TEXT("Player: %s (ID: %d, Score: %.1f)"), *Name, Id, Score);
            
            return ESQLitePreparedStatementExecuteRowResult::Continue;
        });
    
    // 关闭数据库
    Database.Close();
}
```

### 预编译语句 — 带参数绑定的查询

```cpp
FSQLiteDatabase Database;
Database.Open(TEXT("/path/to/my.db"));

// 准备带参数的预编译语句（可复用，性能更优）
FSQLitePreparedStatement InsertStmt;
InsertStmt.Create(Database, TEXT("INSERT INTO Players (Name, Score) VALUES (@Name, @Score)"));

// 绑定参数并执行
InsertStmt.SetBindingValueByName(TEXT("@Name"), FString(TEXT("Bob")));
InsertStmt.SetBindingValueByIndex(2, 100.0f);  // 第 2 个绑定索引对应 @Score
InsertStmt.Execute();
InsertStmt.Reset();       // 重置以便再次使用（不清除绑定）
InsertStmt.ClearBindings(); // 清除所有绑定

// 预编译查询语句
FSQLitePreparedStatement QueryStmt;
QueryStmt.Create(Database, TEXT("SELECT Name, Score FROM Players WHERE Score > @MinScore"));
QueryStmt.SetBindingValueByName(TEXT("@MinScore"), 90.0);

int64 Rows = QueryStmt.Execute([&](const FSQLitePreparedStatement& Stmt) -> ESQLitePreparedStatementExecuteRowResult
{
    FString Name;
    double Score;
    Stmt.GetColumnValueByIndex(0, Name);
    Stmt.GetColumnValueByIndex(1, Score);
    
    UE_LOG(LogTemp, Log, TEXT("High scorer: %s (%.1f)"), *Name, Score);
    return ESQLitePreparedStatementExecuteRowResult::Continue;
});

QueryStmt.Destroy();
InsertStmt.Destroy();
Database.Close();
```

### 类型安全预编译语句 — 宏定义

SQLiteCore 提供宏来定义类型安全的预编译语句，在编译期绑定列和参数类型：

```cpp
// 定义类型安全的预编译语句类型（带列和绑定）
SQLITE_PREPARED_STATEMENT(
    FSelectPlayerById,                           // 类型名
    "SELECT Name, Score FROM Players WHERE Id = @Id",  // SQL
    SQLITE_PREPARED_STATEMENT_COLUMNS(FString, float),  // 输出列类型
    SQLITE_PREPARED_STATEMENT_BINDINGS(int32)            // 绑定参数类型
);

// 使用
FSQLiteDatabase Database;
Database.Open(TEXT("/path/to/my.db"));

FSelectPlayerById SelectStmt(Database);

// 设置绑定值并获取单行结果
FString PlayerName;
float PlayerScore;
bool bSuccess = SelectStmt.BindAndExecuteSingle(123, PlayerName, PlayerScore);

// 或者使用回调枚举多行结果
SelectStmt.SetBindingValueByIndex(1, 42);
SelectStmt.Execute([](const FSelectPlayerById& Stmt) -> ESQLitePreparedStatementExecuteRowResult
{
    FString Name;
    float Score;
    Stmt.GetColumnValues(Name, Score);
    UE_LOG(LogTemp, Log, TEXT("Player: %s, Score: %.1f"), *Name, Score);
    return ESQLitePreparedStatementExecuteRowResult::Continue;
});

SelectStmt.Destroy();
Database.Close();
```

### 数据库元信息操作

```cpp
FSQLiteDatabase Database;
Database.Open(TEXT("/path/to/my.db"));

// 设置/获取用户版本号（常用于数据库 schema 版本迁移）
Database.SetUserVersion(2);
int32 Version;
Database.GetUserVersion(Version);

// 设置/获取应用 ID
Database.SetApplicationId(0x12345678);
int32 AppId;
Database.GetApplicationId(AppId);

// 数据库完整性检查
bool bHealthy = Database.PerformQuickIntegrityCheck();

// 获取数据库文件路径
FString Path = Database.GetFilename();
```

### Blob 数据处理

```cpp
FSQLitePreparedStatement Stmt;
Stmt.Create(Database, TEXT("INSERT INTO Files (Name, Data) VALUES (@Name, @Data)"));

// 绑定二进制数据
TArray<uint8> FileData = { 0x01, 0x02, 0x03, 0x04 };
Stmt.SetBindingValueByName(TEXT("@Name"), FString(TEXT("test.bin")));
Stmt.SetBindingValueByName(TEXT("@Data"), MakeArrayView(FileData), true);  // true = 复制数据
Stmt.Execute();

// 读取 Blob
Stmt.Create(Database, TEXT("SELECT Data FROM Files WHERE Name = @Name"));
Stmt.SetBindingValueByName(TEXT("@Name"), FString(TEXT("test.bin")));
Stmt.Execute([&](const FSQLitePreparedStatement& InStmt) -> ESQLitePreparedStatementExecuteRowResult
{
    TArray<uint8> OutData;
    InStmt.GetColumnValueByIndex(0, OutData);
    // 使用 OutData...
    return ESQLitePreparedStatementExecuteRowResult::Continue;
});

// 也可以绑定 GUID
FGuid MyGuid = FGuid::NewGuid();
Stmt.SetBindingValueByName(TEXT("@Guid"), MyGuid);
FGuid OutGuid;
Stmt.GetColumnValueByName(TEXT("GuidColumn"), OutGuid);
```

## Demo 示例

### MyDatabaseManager.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "SQLiteDatabase.h"
#include "SQLitePreparedStatement.h"

class FMyDatabaseManager
{
public:
    /** 初始化数据库并创建表 */
    bool Initialize(const FString& DatabasePath)
    {
        if (!Database.Open(*DatabasePath, ESQLiteDatabaseOpenMode::ReadWriteCreate))
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open database: %s"), *DatabasePath);
            return false;
        }

        Database.Execute(TEXT(
            "CREATE TABLE IF NOT EXISTS Settings ("
            "  Key TEXT PRIMARY KEY,"
            "  Value TEXT NOT NULL"
            ")"
        ));

        return true;
    }

    /** 写入配置项 */
    bool SetSetting(const FString& Key, const FString& Value)
    {
        FSQLitePreparedStatement Stmt;
        Stmt.Create(Database, TEXT("INSERT OR REPLACE INTO Settings (Key, Value) VALUES (@Key, @Value)"));
        Stmt.SetBindingValueByName(TEXT("@Key"), Key);
        Stmt.SetBindingValueByName(TEXT("@Value"), Value);
        bool bResult = Stmt.Execute();
        Stmt.Destroy();
        return bResult;
    }

    /** 读取配置项 */
    bool GetSetting(const FString& Key, FString& OutValue)
    {
        FSQLitePreparedStatement Stmt;
        Stmt.Create(Database, TEXT("SELECT Value FROM Settings WHERE Key = @Key"));
        Stmt.SetBindingValueByName(TEXT("@Key"), Key);

        bool bFound = false;
        Stmt.Execute([&](const FSQLitePreparedStatement& InStmt) -> ESQLitePreparedStatementExecuteRowResult
        {
            InStmt.GetColumnValueByIndex(0, OutValue);
            bFound = true;
            return ESQLitePreparedStatementExecuteRowResult::Stop;  // 只取第一行
        });

        Stmt.Destroy();
        return bFound;
    }

    /** 关闭数据库 */
    void Shutdown()
    {
        Database.Close();
    }

private:
    FSQLiteDatabase Database;
};
```

### MyDatabaseManager.cpp

```cpp
#include "MyDatabaseManager.h"
```

### 使用示例

```cpp
FMyDatabaseManager Manager;
Manager.Initialize(FPaths::ProjectSavedDir() / TEXT("Settings.db"));
Manager.SetSetting(TEXT("LastLevel"), TEXT("MainMenu"));
Manager.SetSetting(TEXT("MusicVolume"), TEXT("0.8"));

FString Level;
Manager.GetSetting(TEXT("LastLevel"), Level);  // Level == "MainMenu"

Manager.Shutdown();
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine 等）。SQLite 库本身已随引擎源码附带在 `Engine/Source/ThirdParty/sqlite/` 下。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `d1f697a8` | [Backout] - CL53616706 | 回退了一次变更（可能与编译器警告配置相关） |
| 2026-05-12 | `92e8cec9` | UnrealBuildTool: Enable CastFunctionTypeMismatchWarningLevel as error by default in the build settin | 全局构建配置变更，非插件功能性修改 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 将 UE_LOG 迁移为 UE_LOGF 格式化宏 |
| 2025-10-31 | `6f21cd1e` | Fixed comment | 修复注释文字 |
| 2025-10-31 | `c57f0b00` | Clarified that the output param of Step was only filled for error cases, and not when a row is retur | 澄清 Step() 的 OutErrorCode 参数仅在错误时填充，正常返回行时不填充 |

### 维护评价

SQLiteCore 是一个**稳定且低维护**的底层基础设施插件。自 2019 年创建以来，它围绕 SQLite C 库的封装已趋于成熟，近年的提交主要集中在注释修正、日志宏迁移等非功能性改动，说明核心 API 已经稳定。该插件仅用于 Epic 内部服务程序（Multi-User Server、LiveLink Hub 等），不面向普通游戏项目，因此更新频率低是正常现象。

**推荐程度**：如果你的项目确实属于 `SupportedPrograms` 范围内的服务程序，或者你能在自定义程序中手动启用此插件，它是一个成熟可靠的嵌入式数据库方案。对于普通游戏项目，该插件默认未启用且不在官方支持范围内，建议谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Database/SQLiteCore)
- [SQLite 官方文档](https://www.sqlite.org/docs.html)
- [SQLite 许可证（引擎内）](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Source/ThirdParty/Licenses/SQLite_v3.47.1.license)