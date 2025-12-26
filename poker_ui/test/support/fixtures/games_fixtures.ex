defmodule PokerUi.GamesFixtures do
  @moduledoc """
  This module defines test helpers for creating
  entities via the `PokerUi.Games` context.
  """

  @doc """
  Generate a game.
  """
  def game_fixture(attrs \\ %{}) do
    {:ok, game} =
      attrs
      |> Enum.into(%{
        pot: 42,
        title: "some title"
      })
      |> PokerUi.Games.create_game()

    game
  end
end
