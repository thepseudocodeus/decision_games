defmodule PokerUi.Repo.Migrations.AddGameLogicFields do
  use Ecto.Migration

  def change do
    alter table(:games) do
      add :state, :string, default: "lobby"
      add :player_hand, {:array, :string}, default: []
      add :community_cards, {:array, :string}, default: []

      add :win_probability, :float, default: 0.0
    end
  end
end
